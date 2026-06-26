"""
Functions for running the following pipeline:

(Using full-image coregistered (to reference image) (anatomical-anatomical coregistration) images)

- Create transformation files 

- normalize image to MNISym
    - images that we have normalized: T1, segmentations (GM, WM, CSF)
"""

# need path to root directory
import sys
sys.path.append('/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/')


# Imports

import pandas as pd

from image_processing import tissue_extractor as te
import smarts_cerebellum.globals as gl

from pathlib import Path
import os


anat_dir = os.path.join(gl.baseDir, 'anatomicals')
p_df = pd.read_csv(f'{gl.baseDir}/participants_anat.tsv', sep = '\t')


# this function can just do the subject-week loop and return subj_id, week
def _subj_week_loop(df = p_df):
    for i in range(0, df.shape[0]):
        p_id = df['ID'].iloc[i]
        week = (df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(df['Centre'].iloc[i])).strip()
        subj_id = f'{p_centre.strip()}_{p_id}'

        # return each subj_id, week one at a time
        yield subj_id, week
    


def generate_MNISym_coreg_transformation_files(df=p_df):
    """
    Function to get transformation files.
    
    These transformation files are for:
        - full-image coregistered images in MNI Symmetric template.
    
    Only need to generate these files once; then, they can be used to normalize any other image (e.g. segmentation, T1 anatomical)
    """
    for subj, week in _subj_week_loop(df):
        t1_path = f'{anat_dir}/{subj}/{week}/{subj}_{week}_T1.nii'
        mask_path = f'{anat_dir}/{subj}/{week}/{subj}_{week}_T1_cerebellum_dseg.nii.gz'

        if not Path(t1_path).is_file():
            print(f'T1 path does not exist for {subj} in week {week}')
            continue

        if not Path(mask_path).is_file():
            print(f'mask path does not exist for {subj} in week {week}')
            continue

        # make path if it doesn't exist
        results_path = Path(gl.baseDir)/'MNISym/full_img_coreg'/subj/week
        #results_path.mkdir(parents=True) # exist_ok = True (if directory doesn't already exist)

        te.normalize(t1_path, mask_path, results_path, space = 'MNI152NLin2009cSymC')

        print(f'{subj} {week} normalization done \n')
        
    



def normalize_coreg_to_MNISym(
        segment,
        df = p_df
        ):
    
    """
    This function can be used to reslice any image from native (aligned_anatomical - full-image coregistered) space to MNISymmetric space.
    """
    
    tissue_dict = {
        'GM': 'c1',
        'WM': 'c2',
        'CSF': 'c3',
        'T1': '' # T1 anatomicals (basic file) don't have a prefix
    }
    for subj, week in _subj_week_loop(df):

        # files required for reslice: image to-be-normalized (T1 or segment); mask; forward deformation
        img_path = f'{anat_dir}/{subj}/{week}/{tissue_dict[segment]}{subj}_{week}_T1.nii'
        mask_path = f'{anat_dir}/{subj}/{week}/{subj}_{week}_T1_cerebellum_dseg.nii.gz'
        fwd_def = f'{gl.baseDir}/MNISym/full_img_coreg/{subj}/{week}/{subj}_{week}_T1_to-MNI152NLin2009cSymC_mode-image_xfm.nii.gz'

        # check that paths exist
        if not Path(img_path).is_file():
            print(f'{segment} path does not exist for {subj} in week {week}')
            continue
            
        if not Path(mask_path).is_file():
            print(f'mask path does not exist for {subj} in week {week}')
            continue

        if not Path(fwd_def).is_file():
            print(f'fwd def path does not exist for {subj} in week {week}')
            continue

        # path to save images to - as flat folder for each subject
        results_path = f'{gl.baseDir}/MNISym_{segment}/{subj}'
        results_path = Path(results_path)

        #results_path.mkdir(parents = True) # only if necessary
        #results_path.mkdir(parents=True, exist_ok = True)

        # suffix for saving files
        suffix = f'{week}_MNISym_{segment}_coreg'
        # file from relice will be saved as {subj_id}_{suffix}_reslice.nii.gz in results_path
        # FOR NOW (June 26, 9:59am): te.reslice saves image with just the subj_id, so you need to supply weeks if needed.
            # file from relice will be saved as {subj_id}_{suffix}_reslice.nii.gz in results_path

        # run the reslice function to make normalized files
        te.reslice(img_path = img_path,
                   fwd_def = fwd_def,
                   mask_path = mask_path,

                   results_path = results_path,
                   subj_id = subj,
                   suffix = suffix,
                   week = week)
        
        print(f'Normalization of {segment} done for {subj} {week}')
