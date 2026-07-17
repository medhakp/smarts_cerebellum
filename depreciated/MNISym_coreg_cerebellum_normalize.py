# UNDER CONSTRUCTION

"""
Functions for running the following pipeline:

(Using cerebellum-only coregistered images)*

- normalize image to MNISym
    - images that we have normalized: T1, segmentations (GM, WM, CSF)

Store these transformation files in smarts_cerebellum/MNISym/cerebellum_coreg

* from pipeline cerebellar_alignment:
    - create cerebellum-only image
    - (go to matlab, use SPM) coregister cerebellum-only images to each subject's reference image
    - we can either assign the affine to each segmentation INDIVIDUALLY and save it (not good, too much storage) OR
    - in THIS pipeline, take the affine from coregistered cerebellum images and load other images, locally assign the affine to the loaded image, use that
        So we don't actually save the same image with a different affine; we just have cerebellum-only image.

    - also, perhaps our cerebellum-only images should be in the same directory (so not their own folder, just with the other subject-week files)

    - so for this: make a cerebellar_alignment script (directs you to SPM when necessary); output: aligned cerebellum-only images
    (Ask Marco: maybe we can make a folder called "cerebellar_alignment" for this script and the matlab one?)
    - then, work on this pipeline that LOCALLY assigns the affine to the image being worked with (make a function called LOCAL affine assignment) --> local_affine_assignment
"""

"""
THE FIRST THING TO DO FOR THIS PIPELINE IS MOVE OUR CEREBELLAR-ONLY COREGISTERED IMAGES INTO THE SAME ANATOMICALS DIRECTORY AS THE OTHER IMAGES
"""

# need path to root directory
import sys
sys.path.append('/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/')


# Imports

import pandas as pd
import nibabel as nib
from pathlib import Path
import os

import smarts_cerebellum.globals as gl

"""
Requirements:
    - cerebellum-only image coregistered to the reference - for its affine
"""

# so this function shouldn't be called by itself - it should be called in other functions, any time an image is being used
def _local_affine_assignment(source_img_path, target_img_path):
    """
    Function to locally assign affine - i.e. affine-updated image is not *saved*, but loaded into (memory?) to be used here

    Updates affine and s-form matrix of source image

    Inputs:
        source_img_path (str): image to be updated
        target_img_path (str): (coregistered) image with affine to be used

    Outputs:
        source_img (Nifti1Image): source image with updated affine
    """

    source_img = nib.load(source_img_path)
    target_img = nib.load(target_img_path)

    # get (cerebellum-) coregistered affine, sform
    target_affine = target_img.affine
    target_sform = target_img.get_sform()

    # update affine, sform on source image
    source_img.affine[:] = target_affine
    source_img.set_sform(target_sform)

    return source_img


"""
This pipeline is the same as MNISym_coreg_normalize and MNISym_coreg_regression:
    First get the transformation files for the T1 anatomical, then normalize the images requested
    Then, go through the regression pipeline. --> MAKE SURE TO USE THE UPDATED_AFFINE IMAGES
        - once the image is in MNISym template space (i.e. run through the first pipeline), it should have used the correct affine (new affine)
        - so from there, we should be good to just go business-as-usual
"""

def MNISym_cerebellum_coreg_normalize():
    pass