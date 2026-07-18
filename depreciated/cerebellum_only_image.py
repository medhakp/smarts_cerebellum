"""
Create a cerebellum-only image (of T1 anatomical).
"""
import nibabel as nib

def cerebellum_only_img(cerebellar_mask,
                        anat_img,
                        ):
    """
    Creates a cerebellum-only image.
    Inputs:
        cerebellar_mask: binary mask of the cerebellum (Nifti or str)
        anat_img: (T1) anatomical whole-brain image (Nifti or str)
        results_path: directory to store resulting image (str)
    
    Performs element-wise multiplication.

    Output:
        cerebellum-only image (Nifti)
    """

    # load as Nifti image if given string for path
    if type(cerebellar_mask) == str:
        cerebellar_mask = nib.load(cerebellar_mask)

    if type(anat_img) == str:
        anat_img = nib.load(anat_img)

    # get voxel data
    cerebellar_mask_arr = cerebellar_mask.get_fdata()
    anat_arr = anat_img.get_fdata()

    # get within-cerebellum-only voxels
    cerebellar_arr = anat_arr*cerebellar_mask_arr

    """
    Element-wise multiplication (using *) rather than matrix multiplication, so commutes.
    """

    # save as Nifti and save
    cerebellar_img = nib.Nifti1Image(cerebellar_arr, anat_img.affine)
    # this affine will be overwritten by new affine for re-coregistration

    #nib.save(cerebellar_img, f'{results_path}/{subj_id}_{week}_T1_cerebellum_only.nii')
    # save uncompressed so that it can be used in SPM coreg

    return cerebellar_img

