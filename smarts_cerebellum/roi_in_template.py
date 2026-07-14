#%%
import nibabel as nib
import numpy as np
import smarts_cerebellum.globals as gl
import nitools as nt

def roi_in_template(vals, save_name, roi_path, template_path):
    """
    saves file as Nifti (uncompressed)
    """
    roi = nib.load(roi_path)
    template = nib.load(template_path)
    template_arr = template.get_fdata()

    # resample ROI image to template: now, ROI is only where the template exists (in-bounds with template) - so cerebellum-only
    i, j, k = np.indices(template.shape)
    x,y,z = nt.affine_transform(i, j, k, template.affine)
    roi_template = nt.sample_image(roi, x, y,z, interpolation = 0) # use nearest-neighbour for discrete values

    # get relevant tracts
    tract_vals = np.isin(roi_template, vals) # find voxels with that tract's values (labels)
    tract_arr = np.where(tract_vals, roi_template, 0) # set tracts with other labels to 0 in roi

    # if cerebellar template has zero value in a voxel, set tract value to zero as well
    cereb_tract_arr = np.where(template_arr!=0, tract_arr, 0)
 

    # there seem to be some rounding issues - this array has 13.9999...7 instead of 14, for example
    # maybe bc dtype is float? Try rounding up to nearest int (ceil)
    cereb_tract_arr = np.ceil(cereb_tract_arr).astype(int)

    # save image with template affine
    cereb_tract = nib.Nifti1Image(cereb_tract_arr, template.affine, template.header)
    nib.save(cereb_tract, f'{gl.baseDir}/ROI/{save_name}.nii')




# our call
roi_path = f'{gl.baseDir}/ROI/xtract-tract-atlases-maxprob5-1mm.nii.gz'
template_path = f'{gl.baseDir}/ROI/tpl-MNI152NLin2009cSymC_T1w.nii'

cst_vals = [14, 15]
save_name = 'CST.MNI'

roi_in_template(vals = cst_vals, save_name = save_name, roi_path = roi_path, template_path = template_path)


# %%
