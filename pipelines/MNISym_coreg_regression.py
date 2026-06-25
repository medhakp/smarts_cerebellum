import numpy as np
import pandas as pd

import nibabel as nib

import smarts_cerebellum.globals as gl
from smarts_cerebellum import regression, mirror_lesion, template_overall_image, make_summarized_dataframe

from pathlib import Path
import os


p_df = pd.read_csv(f'{gl.baseDir}/participants_anat.tsv', sep = '\t')


#______________________________________________________________________
patients_df = p_df[p_df.isPatient == 1]
controls_df = p_df[p_df.isPatient == 0]

left_lesion_df = p_df[p_df.LesionSide == 'left ']



# change to web path
template_path = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'

template_img = nib.load(template_path)
template_affine = template_img.affine

reg_path = f'{gl.baseDir}/Regression'

means_dir = f'{gl.baseDir}/Regression/mean_images'
medians_dir = f'{gl.baseDir}/Regression/median_images'
#______________________________________________________________________

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
        ref_img = f'{gl.baseDir}/MNISym_{type}/{subj}/{subj}_{refT1}_MNISym_{type}_coreg_reslice.nii.gz'

        print(f"Regression on {subj} \n")

        intercept_img, slope_img = regression.perform_regression_week(subj_id = subj,
                            reference_img = ref_img
                            )
        

        # if images exist, save them
        if intercept_img is not None and slope_img is not None:
            results_path = f'{gl.baseDir}/Regression/{subj}'
            results_path = Path(results_path)

            # comment this out if this directory already exists
            #results_path.mkdir(parents = True, exist_ok = True)

            nib.save(intercept_img, f'{results_path}/{subj}_MNISym_{type}_coreg_reslice_intercept.nii.gz')
            nib.save(slope_img, f'{results_path}/{subj}_MNISym_{type}_coreg_reslice_slope.nii.gz')


def mean_image_right(segment, df):
    """
    @Authors: Marco,
    """
    counter = 0

    left_lesion_df = df[df.LesionSide == 'left ']
    
    # empty array in the shape of the slope image
    slope = np.zeros((template_img.get_fdata()).shape)

    for subj in df.subj_id.unique():
        
        subj_dir = f'{gl.baseDir}/Regression/{subj}'
        subj_slope = f'{subj_dir}/{subj}_MNISym_{segment}_coreg_reslice_slope.nii.gz'

        if not Path(subj_slope).exists():
            print(f'skipped {subj}')
            continue

        subj_slope_img = nib.load(subj_slope)


        if subj in left_lesion_df.subj_id.unique():
            # flip slope
            subj_slope_img = mirror_lesion.FlipLR(subj_slope_img)

        
        subj_slope_arr = subj_slope_img.get_fdata()


        # add each image to the overall slope image
        slope +=subj_slope_arr
        counter +=1 # number of slope matrices used
        
    # average
    slope = slope/counter

    return slope


def median_image_right(segment, df):
    """
    @Authors: Marco,
    """

    arrays = [] # tuple of (slope) tensors
    
    left_lesion_df = df[df.LesionSide == 'left ']

    
    # empty array in the shape of the slope image
    slope = np.zeros((template_img.get_fdata()).shape)

    for subj in df.subj_id.unique():
        
        subj_dir = f'{gl.baseDir}/Regression/{subj}'
        subj_slope = f'{subj_dir}/{subj}_MNISym_{segment}_coreg_reslice_slope.nii.gz'

        if not Path(subj_slope).exists():
            print(f'skipped {subj}')
            continue

        subj_slope_img = nib.load(subj_slope)

        if subj in left_lesion_df.subj_id.unique():
            # flip slope
            subj_slope_img = mirror_lesion.FlipLR(subj_slope_img)

            
        arrays.append(subj_slope_img.get_fdata())
    
    # stack arrays to get median
    slope = np.median(np.stack(arrays, axis = 0), axis = 0)
    return slope



def flip_left_lesion(path, left_lesion_df, space='MNISym', segment='T1', metric='slope'):
    '''
    flip left lesion to the right
    '''

    for subj in left_lesion_df.subj_id.unique():

        flip = f'{path}/{subj}/{subj}_{space}_{segment}_coreg_reslice_{metric}.nii.gz'
        if not Path(flip).is_file():
            print(f'Skip {subj}')
            continue
        flipped = mirror_lesion.FlipLR(flip)
        nib.save(flipped, f'{path}/{subj}/{subj}_{space}_{segment}_coreg_reslice_{metric}_FlipLR.nii.gz')



# use flipped images where necessary
suffixes = [
    'MNISym_CSF_coreg_reslice_slope.nii.gz',
    'MNISym_logJac_coreg_reslice_slope.nii.gz',
    'MNISym_WM_coreg_reslice_slope.nii.gz',
    'MNISym_GM_coreg_reslice_slope.nii.gz',
    'MNISym_T1_coreg_reslice_slope.nii.gz'
]

flipped_suffixes = [
    'MNISym_CSF_coreg_reslice_slope_FlipLR.nii.gz',
    'MNISym_logJac_coreg_reslice_slope_FlipLR.nii.gz',
    'MNISym_WM_coreg_reslice_slope_FlipLR.nii.gz',
    'MNISym_GM_coreg_reslice_slope_FlipLR.nii.gz',
    'MNISym_T1_coreg_reslice_slope_FlipLR.nii.gz'
]


# REGRESSION
subj_unique_regression_MNISym_coreg('T1')
subj_unique_regression_MNISym_coreg('WM')
subj_unique_regression_MNISym_coreg('GM')
subj_unique_regression_MNISym_coreg('CSF')
subj_unique_regression_MNISym_coreg('logJac')

# MEAN IMAGES - PATIENTS
mean_image_right('T1', patients_df)
mean_image_right('WM', patients_df)
mean_image_right('GM', patients_df)
mean_image_right('CSF', patients_df)
mean_image_right('logJac', patients_df)

# MEDIAN IMAGES - PATIENTS
median_image_right('T1', patients_df)
median_image_right('WM', patients_df)
median_image_right('GM', patients_df)
median_image_right('CSF', patients_df)
median_image_right('logJac', patients_df)

# MEAN IMAGES - CONTROLS
mean_image_right('T1', controls_df)
mean_image_right('WM', controls_df)
mean_image_right('GM', controls_df)
mean_image_right('CSF', controls_df)
mean_image_right('logJac', controls_df)

# MEDIAN IMAGES - CONTROLS
median_image_right('T1', controls_df)
median_image_right('WM', controls_df)
median_image_right('GM', controls_df)
median_image_right('CSF', controls_df)
median_image_right('logJac', controls_df)

flip_left_lesion(path = reg_path, segment = 'T1')
flip_left_lesion(path = reg_path, segment = 'WM')
flip_left_lesion(path = reg_path, segment = 'GM')
flip_left_lesion(path = reg_path, segment = 'CSF')
flip_left_lesion(path = reg_path, segment = 'logJac')

summarized_df = make_summarized_dataframe.make_summarized_dataframe(p_df = p_df,
                               search_path = f'{gl.baseDir}/Regression',
                               the_atlas = 'Diedrichsen_2009',
                               maps = 'atl-Anatom',
                               space = 'MNISym',
                               suffixes = suffixes,
                               flipped_suffixes = flipped_suffixes,
                               flip = 'left'
                               )



