import nibabel as nib
import numpy as np
import smarts_cerebellum.globals as gl
import nitools as nt
import os
import ants

# import not working here, so add its path
import sys
sys.path.append("/home/UWO/mporwal2/Documents/GitHub/Functional_Fusion")
import Functional_Fusion.atlas_map as am

# 1. make atlas cerebellum-only (in its space)
def cerebellum_only_roi(roi_path, template_path):
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

    cereb_tract_arr = np.where(template_arr!=0, roi_template, 0)

    # avoid rounding/floating points in tract labels: round up and save array vals as int
    #cereb_tract_arr = np.ceil(cereb_tract_arr).astype(int)

    cereb_tract = nib.Nifti1Image(cereb_tract_arr, template.affine, template.header)
    return cereb_tract

# 2. warp atlas
def warp_atlas(xtract, source, target, save_path):
    source_img = ants.image_read(source)
    target_img = ants.image_read(target)

    # get only cerebellum + brainstem area in atlas's space
    xtract_cerebellum = cerebellum_only_roi(xtract, source) # returns nifti object
    xtract_cerebellum = ants.from_nibabel_nifti(xtract_cerebellum).astype('float32') # convert nifti object to ants

    # create deformation file from source (atlas) to target space
    reg = ants.registration(fixed = target_img, moving = source_img)

    # use that deformation to warp atlas (interpolator = genericLabel for label images)
    warped_atlas = ants.apply_transforms(fixed = target_img,
                                        moving = xtract_cerebellum,
                                        transformlist = reg['fwdtransforms'],
                                        interpolator = 'genericLabel')
    # save warped atlas
    ants.image_write(warped_atlas, save_path)


# 3. extract relevant tract
def get_tract(labels, roi_path):
    roi = nib.load(roi_path)
    roi_arr = roi.get_fdata()

    tract_arr = np.where(np.isin(roi_arr, labels), # tract vals
                          roi_arr, # in this array, else 0
                          0).astype(np.int16)
    return nib.Nifti1Image(tract_arr, roi.affine)
  

# optional: get left/right tracts (if needed, e.g. MCP given bilaterally)
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

# optional: cut roi into segments
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


def make_roi(roi, roi_path, save_name):
    if roi == 'CST':
        cst_vals = [14, 15]
        save_name = 'MNISymC.CST'
        cereb_tract = get_tract(cst_vals, roi_path)
        nib.save(cereb_tract, f'{gl.baseDir}/ROI/{save_name}.nii')
    elif roi == 'MCP_with_ventral_pons':
        mcp_vals = [26]
        save_name = 'MNISymC.MCP_with_ventral_pons'

        cereb_tract = get_tract(mcp_vals,roi_path)
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

    xtract = os.path.join(gl.baseDir, 'ROI', 'xtract-tract-atlases-maxprob5-1mm.nii.gz')
    source = os.path.join(gl.baseDir, 'ROI', 'cerebellar_atlases', 'tpl-MNI152NLin6AsymC', 'tpl-MNI152NLin6AsymC_T1w.nii') # "moving"; use cerebellum-only template
    target = os.path.join(gl.baseDir, 'ROI', 'tpl-MNI152NLin2009cSymC_T1w.nii') # "fixed"
    warped_path = os.path.join(gl.baseDir, 'ROI', 'MNISymC.xtract.nii')

    # 1. warp atlas (only once)
    warp_atlas(xtract=xtract, source=source, target=target, save_path=warped_path)

    # make each ROI
    roi = 'CST'
    roi_save_name = f'MNISymC.{roi}'
    make_roi(roi = roi, roi_path = warped_path, save_name=roi_save_name)
    # MCP (no ventral pons): set y = 76; then scroll up in y, remove anything at y>76; save as MNISymC.nii
 