# these functions have been generalized and moved to smarts_cerebellum.util - hopefully they work
# then, this file is deprecated

"""
Functions for the following pipeline:

(Using normalized (MNISym template) images):

- run regression on resliced images

- mirror cerebellum images such that all lesions are on right hemisphere
    - i.e. for subjects with LH cerebral lesions, flip (along x-axis) their slope image

- calculate average image
"""

import sys
sys.path.append('/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/')

# Imports

import numpy as np
import pandas as pd

import nibabel as nib
from nilearn import plotting as npl

import nitools as nt

from smarts_cerebellum import regression
from image_processing import overall_image
from image_processing import mirror_lesion

from pathlib import Path
import os

# directories
base_dir = '/cifs/diedrichsen/data/smarts_cerebellum'
p_df = pd.read_csv('/cifs/diedrichsen/data/smarts_cerebellum/participants_anat.tsv', sep = '\t')


# this has been made into a general function in smarts_cerebellum.util - call it from there
# as input, you need: subdir (folder), suffix (image_name) - so you can put those in the notebook as insertables with type (since otherwise the name is the exact same)
"""
ref_img = f'{base_dir}/MNISym_{type}/{subj}/{subj}_{refT1}_MNISym_{type}_coreg_reslice.nii.gz'
This is in the format:
    path: smarts_cerebellum/subdir/subj
    image: subj_refT1_suffix.nii.gz where suffix = MNISym_{type}_coreg_reslice, so we can just have {type} as an insertable in the notebook

results_path = f'{base_dir}/Regression/{subj}'
nib.save(intercept_img, f'{results_path}/{subj}_MNISym_{type}_coreg_reslice_intercept.nii.gz')
nib.save(slope_img, f'{results_path}/{subj}_MNISym_{type}_coreg_reslice_slope.nii.gz')
These are as:
    path: smarts_cerebellum/Regression/subj
    image: subj_suffix_intercept/slope.nii.gz where suffix is exactlyt he same as the input image.


"""
def subj_unique_regression_MNISym_coreg(type):

    """
    
    Function for local use.

    Function to perform regression on coregistered and normalized (to MNISym template) images

    Input:
        type (str): type of image; used for finding image and for saving images
            valid types: GM, WM, T1
            TBA: CSF
    """

    for subj in p_df['subj_id'].unique():

        # find each subject's reference image, and run it through the regression
        refT1 = (p_df.loc[(p_df['subj_id']==subj), 'RefT1'].iloc[0]).strip()
        ref_img = f'{base_dir}/MNISym_{type}/{subj}/{subj}_{refT1}_MNISym_{type}_coreg_reslice.nii.gz'

        print(f"Regression on {subj} \n")

        intercept_img, slope_img = regression.perform_regression_week(subj_id = subj,
                            reference_img = ref_img
                            )
        

        # if images exist, save them
        if intercept_img is not None and slope_img is not None:
            results_path = f'{base_dir}/Regression/{subj}'
            results_path = Path(results_path)

            # comment this out if this directory already exists
            #results_path.mkdir(parents = True, exist_ok = True)

            nib.save(intercept_img, f'{results_path}/{subj}_MNISym_{type}_coreg_reslice_intercept.nii.gz')
            nib.save(slope_img, f'{results_path}/{subj}_MNISym_{type}_coreg_reslice_slope.nii.gz')


# name will be like <subj_id>_MNISym_GM_reslice_<alg = intercept/slope>.nii.gz

# this is in smarts_cerebellum.util
def subj_unique_flip(df, image_suffix, output_suffix = 'FlipLR'):
    """
    Flips specified image along the x-axis

    Image will be saved as {subj}_{image_suffix}_{output_suffix}.nii.gz
    """

    for subj in df['subj_id'].unique():
        image_to_flip = f'{base_dir}/Regression/{subj}/{subj}_{image_suffix}.nii.gz'

        if not Path(image_to_flip).exists():
            print(f'path does not exist for {subj}; skipping')
            continue
        
        flipped_img = mirror_lesion.FlipLR(image_to_flip)
        print(f'Flipped image for {subj}')

        # save flipped image
        nib.save(flipped_img, f'{base_dir}/Regression/{subj}/{subj}_{image_suffix}_{output_suffix}.nii.gz')
        


# use the template for image properties: affine, voxel array shape.

# add this to notebook maybe? Not sure.
template_path = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'
template_img = nib.load(template_path)
template_affine = template_img.affine


# put mean_image in its own function. --> make these in overall images? And the call in utils
def mean_image_right(df, suffix):
    """
    @Authors: Marco,
    """
    counter = 0
    
    # empty array in the shape of the slope image
    slope = np.zeros((template_img.get_fdata()).shape)

    for subj in df.subj_id.unique():
        
        subj_dir = f'{base_dir}/Regression/{subj}'
        subj_slope = f'{subj_dir}/{subj}_{suffix}.nii.gz'

        if not Path(subj_slope).exists():
            print(f'skipped {subj}')
            continue

        subj_slope_img = nib.load(subj_slope)

        subj_df = df[df.subj_id == subj]

        if (subj_df.iloc[0]['LesionSide']).strip() == 'left':
            # flip slope
            subj_slope_img = mirror_lesion.FlipLR(subj_slope_img)

        
        subj_slope_arr = subj_slope_img.get_fdata()


        # add each image to the overall slope image
        slope +=subj_slope_arr
        counter +=1 # number of slope matrices used
        
    # average
    slope = slope/counter

    return slope


def median_image_right(df, suffix):
    """
    @Authors: Marco,
    """

    arrays = [] # tuple of (slope) tensors
    
    # empty array in the shape of the slope image
    slope = np.zeros((template_img.get_fdata()).shape)

    for subj in df.subj_id.unique():
        
        subj_dir = f'{base_dir}/Regression/{subj}'
        subj_slope = f'{subj_dir}/{subj}_{suffix}.nii.gz'

        if not Path(subj_slope).exists():
            print(f'skipped {subj}')
            continue

        subj_slope_img = nib.load(subj_slope)

        subj_df = df[df.subj_id == subj]

        if (subj_df.iloc[0]['LesionSide']).strip() == 'left':
            # flip slope
            subj_slope_img = mirror_lesion.FlipLR(subj_slope_img)
            
        arrays.append(subj_slope_img.get_fdata())
    
    # stack arrays to get median
    slope = np.median(np.stack(arrays, axis = 0), axis = 0)
    return slope