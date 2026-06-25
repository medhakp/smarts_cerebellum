"""
This file contains calls for functions in smarts_cerebellum

This can be used in pipelines.

All calls are general, so they work for any tile, in any directory; just need to specify.
"""

import numpy as np
import pandas as pd

import nibabel as nib
from pathlib import Path

# smarts_cerebellum functions
from smarts_cerebellum import mirror_lesion
from smarts_cerebellum import regression

# base directory for project, participants tsv
import smarts_cerebellum.globals as gl


base_dir = gl.baseDir
p_df = pd.read_csv(f'{base_dir}/participants_anat.tsv', sep = '\t')

"""
Make this a general function call: the only part that is specific to MNISym_coreg is the path name, so have a general path name.
Then, when we call it in MNISym_coreg_regression pipeline, we can just have the path defined before we call the function, and have an insertable "type".
"""
def subj_unique_regression_week(subdir, suffix):

    """
    General call for regression function (voxel-wise regression on each subject's weeks).
    Saves intercept and slope images to specified path inside smarts_cerebellum/Regression/{subj} for each subject

    Input:
        type (str): type of image; used for finding image and for saving images
            valid types: GM, WM, T1, CSF
        subdir (str): directory containing subject folders inside smarts_cerebellum
        suffix (str): image suffix

        (Image path follows structure: smarts_cerebellum/{subdir}/{subj}/{subj}_{refT1}_{suffix}.nii.gz)
        Image saved:
            folder: smarts_cerebellum/Regression/{subj}
            image_name: {subj}_{suffix}_{intercept/slope}

    **If getting error "path not exist", uncomment the line to make results_path**
    This assumes that the results path (smarts_cerebellum/Regression/subj) exists

    """

    for subj in p_df['subj_id'].unique():

        # find each subject's reference image, and run it through the regression
        refT1 = (p_df.loc[(p_df['subj_id']==subj), 'RefT1'].iloc[0]).strip()
        ref_img = f'{base_dir}/{subdir}/{subj}/{subj}_{refT1}_{suffix}.nii.gz'

        print(f"Regression on {subj} \n")

        intercept_img, slope_img = regression.perform_regression_week(subj_id = subj,
                            reference_img = ref_img
                            )
        

        # if images exist, save them
        if intercept_img is not None and slope_img is not None:
            #results_path = f'{base_dir}/Regression/{subj}'
            
            results_path = f'{base_dir}/regression_test/{subj}'
            
            results_path = Path(results_path)

            # comment this out if this directory already exists
            #results_path.mkdir(parents = True, exist_ok = True)

            nib.save(intercept_img, f'{results_path}/{subj}_{suffix}_intercept.nii.gz')
            nib.save(slope_img, f'{results_path}/{subj}_{suffix}_slope.nii.gz')




def flip_left_lesion(path, left_lesion_df, suffix):
    '''
    flip left lesion to the right
    
    Inputs:
        path (str): base path to subject files
            image will be found in: f'{path}/{subj}/{subj}_{suffix}.nii.gz'
        left_lesion_df (Pandas dataframe): dataframe containing all participants with left hemisphere lesion - to be flipped!
        suffix (str): image suffix (for image to be flipped)

        Filenames follow convention {subj}_{suffix}.nii.gz
        Output images saved as {subj}_{suffix}_FlipLR.nii.gz
        File path follows convention {path}/{subj}/{file_name}
    
    Image is saved to the directory where the original image is found;
        same name, with 'FlipLR' appended to the name
    '''
  

    for subj in left_lesion_df.subj_id.unique():
        flip_image = f'{path}/{subj}/{subj}_{suffix}.nii.gz'

        # check if file exists
        if not Path(flip_image).is_file():
            print(f'Skip {subj}')
            continue

        # flip image along x-axis (flips left-lesion image to right)
        flipped = mirror_lesion.FlipLR(flip_image)
        
        # save image to specified directory for each subject with 'FlipLR' appended to the end of its name
        nib.save(flipped, f'{path}/{subj}/{subj}_{suffix}_FlipLR.nii.gz')

