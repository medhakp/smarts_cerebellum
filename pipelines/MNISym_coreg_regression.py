"""
MNISym_coreg_regression pipeline

For files that have been (a) full-image coregistered, (b) normalized to MNI Symmetric template

**pipeline**
    - voxel-wise regression

    - get mean and median slope images for each of patients and controls

    - get left_lesion-only images

    - make a summarized dataframe for (mean, median, sum) volume in ROIs defined by atlas "Diedrichsen_2009"
"""

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

def regression_MNISym_coreg(segment):

    """
    
    Function for local use.

    Function to perform regression on coregistered and normalized (to MNISym template) images

    Input:
        segment (str): type of image; used for finding image and for saving images
            valid segments: GM, WM, T1
            TBA: CSF
    """

    for subj in p_df['subj_id'].unique():

        # find each subject's reference image, and run it through the regression
        refT1 = (p_df.loc[(p_df['subj_id']==subj), 'RefT1'].iloc[0]).strip()
        ref_img = f'{gl.baseDir}/MNISym_{segment}/{subj}/{subj}_{refT1}_MNISym_{segment}_coreg_reslice.nii.gz'

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

            nib.save(intercept_img, f'{results_path}/{subj}_MNISym_{segment}_coreg_reslice_intercept.nii.gz')
            nib.save(slope_img, f'{results_path}/{subj}_MNISym_{segment}_coreg_reslice_slope.nii.gz')



# get MEAN slope images
def MNISym_coreg_slope_mean_right(segment, group, df):

    """
    local function for getting mean slope images

    Inputs:
        segment(str): T1, WM, GM, CSF, logJac
        group (str): patients, controls
        df (Pandas dataframe): dataframe for patients or controls
    """
    suffix = f'MNISym_{segment}_coreg_reslice'

    # call mean function
    mean_slope = template_overall_image.mean_image_right(df = df, suffix = suffix, template_img = template_img)
    
    # save image (with affine of template)
    mean_slope_img = nib.Nifti1Image(mean_slope, template_affine)
    nib.save(mean_slope_img, f'{means_dir}/{group}_MNISym_{segment}_coreg_slope_mean.nii')


# get MEDIAN slope images
def MNISym_coreg_slope_median_right(segment, group, df):

    """
    local function for getting median slope images

    Inputs:
        segment(str): T1, WM, GM, CSF, logJac
        group (str): patients, controls
        df (Pandas dataframe): dataframe for patients or controls
    """
    suffix = f'MNISym_{segment}_coreg_reslice'

    # call mean function
    median_slope = template_overall_image.median_image_right(df = df, suffix = suffix, template_img = template_img)
    
    # save image (with affine of template)
    median_slope_img = nib.Nifti1Image(median_slope, template_affine)
    nib.save(median_slope_img, f'{medians_dir}/{group}_MNISym_{segment}_coreg_slope_mean.nii')


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


def MNISym_coreg_summarized_df():
    summarized_df = make_summarized_dataframe.make_summarized_dataframe(p_df = p_df,
                               search_path = f'{gl.baseDir}/Regression',
                               the_atlas = 'Diedrichsen_2009',
                               maps = 'atl-Anatom', # labels from anatomical atlas
                               space = 'MNISym',
                               suffixes = suffixes,
                               flipped_suffixes = flipped_suffixes,
                               flip = 'left'
                               )
    return summarized_df

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
regression_MNISym_coreg('WM')
regression_MNISym_coreg('GM')
regression_MNISym_coreg('CSF')
regression_MNISym_coreg('logJac')
regression_MNISym_coreg('T1')

# MEAN IMAGES - PATIENTS
MNISym_coreg_slope_mean_right('T1', 'patients', patients_df)
MNISym_coreg_slope_mean_right('WM', 'patients', patients_df)
MNISym_coreg_slope_mean_right('GM', 'patients', patients_df)
MNISym_coreg_slope_mean_right('CSF', 'patients', patients_df)
MNISym_coreg_slope_mean_right('logJac', 'patients', patients_df)

# MEDIAN IMAGES - PATIENTS
MNISym_coreg_slope_median_right('T1', 'patients', patients_df)
MNISym_coreg_slope_median_right('WM', 'patients', patients_df)
MNISym_coreg_slope_median_right('GM', 'patients', patients_df)
MNISym_coreg_slope_median_right('CSF', 'patients', patients_df)
MNISym_coreg_slope_median_right('logJac', 'patients', patients_df)

# MEAN IMAGES - CONTROLS
MNISym_coreg_slope_mean_right('T1', 'controls', controls_df)
MNISym_coreg_slope_mean_right('WM', 'controls', controls_df)
MNISym_coreg_slope_mean_right('GM', 'controls', controls_df)
MNISym_coreg_slope_mean_right('CSF', 'controls', controls_df)
MNISym_coreg_slope_mean_right('logJac', 'controls', controls_df)

# MEDIAN IMAGES - CONTROLS
MNISym_coreg_slope_median_right('T1', controls_df)
MNISym_coreg_slope_median_right('WM', controls_df)
MNISym_coreg_slope_median_right('GM', controls_df)
MNISym_coreg_slope_median_right('CSF', controls_df)
MNISym_coreg_slope_median_right('logJac', controls_df)


# FLIP LESION IMAGES WHERE NECESSARY
flip_left_lesion(path = reg_path, segment = 'T1')
flip_left_lesion(path = reg_path, segment = 'WM')
flip_left_lesion(path = reg_path, segment = 'GM')
flip_left_lesion(path = reg_path, segment = 'CSF')
flip_left_lesion(path = reg_path, segment = 'logJac')

# MAKE SUMMARIZED DATAFRAME
summarized_df = MNISym_coreg_summarized_df()
save_df_path = f'{gl.baseDir}/Regression'
summarized_df.to_csv(os.path.join(save_df_path, 'MNISym_coreg_slope_AtlasSUIT_summarized.tsv'), sep='\t', index=False)


