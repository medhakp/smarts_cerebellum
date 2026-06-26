# need path to root directory
import sys
sys.path.append('/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/')


# Imports

import pandas as pd
from pathlib import Path
import os

from image_processing import cerebellum_only_image as coi
import smarts_cerebellum.globals as gl



p_df = pd.read_csv(f'{gl.baseDir}/participants_anat.tsv', sep = '\t')


def _subj_week_loop(df = p_df):
    for i in range(0, df.shape[0]):
        p_id = df['ID'].iloc[i]
        week = (df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(df['Centre'].iloc[i])).strip()
        subj_id = f'{p_centre.strip()}_{p_id}'

        # return each subj_id, week one at a time
        yield subj_id, week




# cerebellum-only image
def get_cerebellum_image(df = p_df):
    for subj, week in _subj_week_loop(df):
        
        # need T1 anatomical and cerebellum isolation mask
        t1_path = f'{gl.baseDir}/anatomicals/{subj}/{week}/{subj}_{week}_T1.nii'
        mask_path = f'{gl.baseDir}/anatomicals/{subj}/{week}/{subj}_{week}_T1_cerebellum_dseg.nii.gz'

        # check that paths exists
        if not Path(t1_path).is_file():
            print(f'mask path does not exist for {subj} in week {week}')
            continue

        if not Path(mask_path).is_file():
            print(f'mask path does not exist for {subj} in week {week}')
            continue

        # cerebellum-only image stored in the same place as other anatomicals.
        results_path = f'{gl.baseDir}/anatomicals/{subj}/{week}'

        # right now, the function saves the mask - perhaps we should do that in here.
        cerebellum_img = coi.cerebellum_only_img(cerebellar_mask = mask_path,
                                                 anat_img = t1_path,
                                                 results_path = results_path,
                                                 subj_id = subj,
                                                 week = week
                                                 )
        print(f'cerebellum-only image for {subj} {week} done')

        
    
