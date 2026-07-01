"""
Assigns affine from target/reference image to a source image (for world-coordinate alignment); data (voxel-coordinates) remain unchanged.
"""

"""
TEST: DO WE ALSO NEED TO UPDATE S/Q FORM MATRICES? TRY WITHOUT UPDATING FIRST.

OR HAVE IT AS AN OPTION TO ALSO UPDATE, UPDATE_SFORM = FALSE BY DEFAULT (UPDATE_QFORM = FALSE BY DEFUALT AS WELL)
"""

# Imports

# image reading libraries
import nibabel as nib
from pathlib import Path


def affine_assignment(
        reference_img,
        source_img,
        
        # image-saving
        results_path,

        
        # subj_id,
        # week,
        # tissue = 'None', # used in name
    
        # optional
        update_sform = False,
        update_qform = False
):
    """
    Inputs:
        reference image (Nifti or str): image containing target affine
        source image (Nifti or str): image with affine to update

        results_path (str): path to store image with updated affine

        # taken out for now; testing
        subj_id, week (str)

        update_sform, update_qform: False by default; updates s-form, q-form matrices of source image with that of reference image.
        ^I don't think these are needed; I think it's already updated when we save the image

    Assigns affine from reference/target image to source image (for world-coordinates alignment).

    Output:
        updated affine source image
    """

    if type(reference_img) == str:
        reference_img = nib.load(reference_img)
    else:
        reference_img = reference_img

    if type(source_img) == str:
        source_img = nib.load(source_img)
    else:
        source_img = source_img

    target_affine = reference_img.affine
    source_img.affine[:] = target_affine

    if update_sform == True:
        target_sform = reference_img.get_sform()
        source_img.set_sform(target_sform)
    if update_qform == True:
        target_qform = reference_img.get_qform()
        source_img.set_qform(target_qform)
        """
        note: here, the ref image might not have qform, in which case, either:
            (a) assign it sform (function update later or manually)
            (b) don't update qform in source image
                (this could be an issue, depending on usage - so check out the qform of the source image!)
        """

    # THIS NEEDS TO BE TESTED; I EXPECT THAT IT'LL WORK FOR JUST .NII EXTENSION
    #source_path = Path(source_img)
    #source_name = Path(reference_img).stem


    # save affine-updated image to specified directory - MAKE SURE THIS IS CORRECT
    # putting in cerebellar_align as a failsafe for now
    #nib.save(source_img, f'{results_path}/{source_name}_cerebellar_align.nii')

    return source_img