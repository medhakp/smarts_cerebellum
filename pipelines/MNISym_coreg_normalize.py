"""
Functions for running the following pipeline:

(Using full-image coregistered (to reference image) (anatomical-anatomical coregistration) images)

- Create transformation files 

- normalize image to MNISym
"""

# need path to root directory
import sys
sys.path.append('/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/')


# Imports
import numpy as np
import pandas as pd

import nibabel as nib
from image_processing import tissue_extractor as te

from pathlib import Path
import os


# directories
base_dir = '/cifs/diedrichsen/data/smarts_cerebellum'
anat_dir = '/cifs/diedrichsen/data/smarts_cerebellum/anatomicals'
p_df = pd.read_csv('/cifs/diedrichsen/data/smarts_cerebellum/participants_anat.tsv', sep = '\t')




# write normalization files for each subject-week (full-image coregistered)
# this just takes the t1_anatomicals and the isolation mask for each subject.

def generate_MNISym_coreg_transformation_files(p_df):
    """
    Function to get transformation files.
    
    These transformation files are for:
        - full-image coregistered images in MNI Symmetric template.
    
    Only need to generate these files once; then, they can be used to normalize any other image (e.g. segmentation, T1 anatomical)
    """

    # loop through all participant rows and get subjects, weeks
    for i in range(0, p_df.shape[0]):

        p_id = p_df['ID'].iloc[i]
        week = (p_df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(p_df['Centre'].iloc[i])).strip()

        subj_id = f'{p_centre.strip()}_{p_id}'

        t1_path = f'{anat_dir}/{subj_id}/{week}/{subj_id}_{week}_T1.nii'
        mask_path = f'{anat_dir}/{subj_id}/{week}/{subj_id}_{week}_T1_cerebellum_dseg.nii.gz'

        # check that paths exist
        if not Path(t1_path).is_file():
            print(f'T1 path does not exist for {subj_id} in week {week}')
            continue

        if not Path(mask_path).is_file():
            print(f'mask path does not exist for {subj_id} in week {week}')
            continue

        # this is a new folder for each subject-week
        results_path = Path(base_dir)/'MNISym/full_img_coreg'/subj_id/week
        results_path.mkdir(parents=True) # exist_ok = True (if directory doesn't already exist)

        te.normalize(t1_path, mask_path, results_path, space = 'MNI152NLin2009cSymC')

        print(f'{subj_id} {week} normalization done \n')




def reslice_loop(
        sub_dir, # e.g. MNISymm_T1
        suffix, # name of normalized image
        tissue = None
        ):
    
    """
    This function can be used to reslice any image from native (aligned_anatomical - full-image coregistered) space to MNISymmetric space.
    """
    
    tissue_dict = {
        'gm': 'c1',
        'wm': 'c2',
        'csf': 'c3'
    }

    # base loop _____________________________________
    for i in range(0, p_df.shape[0]):
        p_id = p_df['ID'].iloc[i]
        week = (p_df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(p_df['Centre'].iloc[i])).strip()
        
        subj_id = f'{p_centre.strip()}_{p_id}'


        # file to be resliced
        if not tissue == None:
            img_path = f'{anat_dir}/{subj_id}/{week}/{tissue_dict[tissue]}{subj_id}_{week}_T1.nii'
        else:
            img_path = f'{anat_dir}/{subj_id}/{week}/{subj_id}_{week}_T1.nii'
        print(f'using {img_path}')

        
        # mask and forward_defromation files (required for normalization)
        mask_path = f'{anat_dir}/{subj_id}/{week}/{subj_id}_{week}_T1_cerebellum_dseg.nii.gz'
        fwd_def = f'{base_dir}/MNISym/full_img_coreg/{subj_id}/{week}/{subj_id}_{week}_T1_to-MNI152NLin2009cSymC_mode-image_xfm.nii.gz'

        # check that paths exist
        if not Path(img_path).is_file():
            print(f'T1 path does not exist for {subj_id} in week {week}')
            continue
            
        if not Path(mask_path).is_file():
            print(f'mask path does not exist for {subj_id} in week {week}')
            continue

        if not Path(fwd_def).is_file():
            print(f'fwd def path does not exist for {subj_id} in week {week}')
            continue
      
            
        # CHECK THIS PART using one subject
        results_path = Path(base_dir)/sub_dir/subj_id
        results_path.mkdir(parents=True, exist_ok = True)
      
        # we will use the week option in reslice, so it will save each week's resliced image to each week's directory
        te.reslice(img_path = img_path,
                   fwd_def = fwd_def,
                   mask_path = mask_path,

                   results_path = results_path,
                   subj_id = subj_id,
                   suffix = suffix,
                   week = week)
        
        if not tissue == None:
            print(f'Normalization done for {subj_id} {week} for {tissue}')
        else:
            print(f'Normalization done for {subj_id} at {week} for T1 anatomical')

