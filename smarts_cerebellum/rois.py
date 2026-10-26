import nibabel as nib
import numpy as np
import smarts_cerebellum.globals as gl
import nitools as nt
import os

# import not working here, so add its path
import sys
sys.path.append("/home/UWO/mporwal2/Documents/GitHub/Functional_Fusion")
import Functional_Fusion.atlas_map as am


def roi_in_template(labels, roi_path, template_path):
    """
    returns Nifti (uncompressed)
    """
    roi = nib.load(roi_path)
    template = nib.load(template_path)
    template_arr = template.get_fdata()

    # resample ROI image to template: now, ROI is only where the template exists (in-bounds with template) - so cerebellum-only
    i, j, k = np.indices(template.shape)
    x,y,z = nt.affine_transform(i, j, k, template.affine)
    roi_template = nt.sample_image(roi, x, y,z, interpolation = 0) # use nearest-neighbour for discrete values

    # get relevant tracts
    tract_vals = np.isin(roi_template, labels)
    tract_arr = np.where(tract_vals, roi_template, 0)

    # if cerebellar template has zero value in a voxel, set tract value to zero as well
    cereb_tract_arr = np.where(template_arr!=0, tract_arr, 0)

    # avoid rounding/floating points in tract labels: round up and save array vals as int
    cereb_tract_arr = np.ceil(cereb_tract_arr).astype(int)

    # save image with template affine
    cereb_tract = nib.Nifti1Image(cereb_tract_arr, template.affine, template.header)
    return cereb_tract
   

def left_right_roi(tract_path, og_label, lr_labels):
    # we can split the array in half and literally do left-right
    # assumes symmetric template
    
    tract = nib.load(tract_path)
    tract_arr = tract.get_fdata()

    middle = tract_arr.shape[0] // 2 # split array into half
    right = np.zeros_like(tract_arr, dtype = bool) # zero-like array instead of just zeroes?
    left = np.zeros_like(tract_arr, dtype = bool)

    right[:middle] = tract_arr[:middle] == og_label # get non-zero elements in the right side of array
    left[middle:] = tract_arr[middle:] == og_label

    # relabel each side
    tract_arr[right] = lr_labels[1]
    tract_arr[left] = lr_labels[0]

    tract_arr = np.ceil(tract_arr).astype(int)

    lr_tract = nib.Nifti1Image(tract_arr, tract.affine, tract.header)
    return lr_tract

def cut_roi(roi_path, z_start, z_end):
    """
    cuts ROI based on z-coordinates
    Usage: cutting CST tract into midbrain, pons, medulla
    """
    roi = nib.load(roi_path)

    # world coordinates
    i, j, k = np.indices(roi.shape)
    x,y,z = nt.affine_transform(i, j, k, roi.affine)
    roi_arr = nt.sample_image(roi, x, y,z, interpolation = 0) # use nearest-neighbour for discrete values

    cut_arr = np.zeros(roi_arr.shape)
    cut_arr[:,:, z_start:z_end+1] = roi_arr[:,:, z_start:z_end+1]

    # avoid rounding/floating points in tract labels: round up and save array vals as int
    cut_arr = np.ceil(cut_arr).astype(int)

    cut_img = nib.Nifti1Image(cut_arr, affine = roi.affine, header = roi.header)
    return cut_img

def warp_atlas(xtract, target, save_path):
    atlas_src = am.AtlasVolumetric('xtract', xtract, structure='brain', space='MNI152NLin6Asym') # current space
    atlas_trg = am.AtlasVolumetric('template', target, structure = 'cerebellum', space = 'MNI152NLin2009cSymC')
    data = atlas_src.read_data(xtract)
    data[np.isnan(data)] = 0
    data_new = am.deform_data(data,atlas_src, atlas_trg, interpolation=0) # deform; use nearest-neighbour for discrete
    data_new[np.isnan(data_new)] = 0
    img = atlas_trg.data_to_nifti(data_new)
    nib.save(img, save_path)


def make_roi(roi, save_path, template):
    if roi == 'CST':
        cst_vals = [14, 15]
        save_name = 'MNISymC.CST'
        cereb_tract = roi_in_template(cst_vals, save_path, template)
        nib.save(cereb_tract, f'{gl.baseDir}/ROI/{save_name}.nii')
    elif roi == 'MCP_with_ventral_pons':
        mcp_vals = [26]
        save_name = 'MNISymC.MCP_with_ventral_pons'

        cereb_tract = roi_in_template(mcp_vals, save_path, template)
        nib.save(cereb_tract, f'{gl.baseDir}/ROI/{save_name}.nii')

        # get left, right MCP tract separately
        tract_path = f'{gl.baseDir}/ROI/MNISymC.MCP_with_ventral_pons.nii'
        og_label = 26 # label of tract - assumed one value
        lr_labels = [4,3] # right = 4, left = 3
        lr_tract = left_right_roi(tract_path, og_label, lr_labels)
        nib.save(lr_tract, tract_path)
    else:
        raise ValueError("invalid roi")

if __name__ == '__main__':
    xtract =  os.path.join(gl.baseDir, 'ROI', 'xtract-tract-atlases-maxprob5-1mm.nii.gz') # source
    template = os.path.join(gl.baseDir, 'ROI', 'tpl-MNI152NLin2009cSymC_T1w.nii') # target
    save_path = os.path.join(gl.baseDir, 'ROI', 'MNISymC.xtract.nii')

    warp_atlas(xtract, template, save_path)

    make_roi('MCP_with_ventral_pons', save_path, template)
    # MCP (no ventral pons): set y = 76; then scroll up in y, remove anything at y>76; save as MNISymC.nii
 