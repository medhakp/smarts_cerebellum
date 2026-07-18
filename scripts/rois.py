import nibabel as nib
import numpy as np
import smarts_cerebellum.globals as gl
import nitools as nt

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
   



# make cerebellum CST ROI in MNISym (MNISymC.CST)
roi_path = f'{gl.baseDir}/ROI/xtract-tract-atlases-maxprob5-1mm.nii.gz'
template_path = f'{gl.baseDir}/ROI/tpl-MNI152NLin2009cSymC_T1w.nii'

cst_vals = [14, 15]
save_name = 'MNISymC.CST'

cereb_tract = roi_in_template(cst_vals, roi_path, template_path)
nib.save(cereb_tract, f'{gl.baseDir}/ROI/{save_name}.nii')
