import nibabel as nib
import numpy as np
import smarts_cerebellum.globals as gl
import nitools as nt
import os
import ants


# 1. make atlas cerebellum-only (in its space)
def _cerebellum_only_roi(roi_path, template_path, thresh = 0.1):
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

    cereb_tract_arr = np.where(template_arr > thresh, roi_template, 0)

    # avoid rounding/floating points in tract labels: round up and save array vals as int
    cereb_tract_arr = np.rint(np.nan_to_num(cereb_tract_arr)).astype(np.int16)

    cereb_tract = nib.Nifti1Image(cereb_tract_arr, template.affine, template.header)
    cereb_tract.set_data_dtype(np.int16)
    return cereb_tract

# 2. warp atlas
def warp_atlas(xtract, source, target, save_path, 
               transform = 'antsRegistrationSyN[s]', # same transformation used in SUITPy normalization
               seed = 1
               ):
    
    source_img = ants.image_read(source)
    target_img = ants.image_read(target)

    # get only cerebellum + brainstem area in atlas's space
    xtract_cerebellum = ants.from_nibabel_nifti(_cerebellum_only_roi(xtract, source)) # convert nifti object to ants
    
    # create deformation file from source (atlas) to target space
    reg = ants.registration(fixed = target_img, moving = source_img,
                            type_of_transform = transform,
                            random_seed = seed
                            )

    # use that deformation to warp atlas (interpolator = genericLabel for label images)
    warped_atlas = ants.apply_transforms(fixed = target_img,
                                        moving = xtract_cerebellum,
                                        transformlist = reg['fwdtransforms'],
                                        interpolator = 'genericLabel')
    
    # round to int
    
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
    # should use world coordinates here
    
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



def make_roi(roi, roi_path):
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
        lr_labels = [3,4] # right = 4, left = 3
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
    # 2. cut cerebellum-only again (in target space)
    atlas_cerebellum = _cerebellum_only_roi(warped_path, target)
    nib.save(atlas_cerebellum, warped_path) # save cut roi to the same path

    # 3. make each ROI
    rois = ['CST', 'MCP_with_ventral_pons']
    for roi in rois:
        make_roi(roi = roi, roi_path = warped_path)
        # 'MNISymC.MCP': MCP (no ventral pons): set y = 76; then scroll up in y, remove anything at y>76; save as MNISymC.nii
    