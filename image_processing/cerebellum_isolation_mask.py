# Imports

import pandas as pd
from pathlib import Path
from image_processing import tissue_extractor as te
import smarts_cerebellum.globals as gl



p_df = pd.read_csv(f'{gl.baseDir}/participants_anat.tsv', sep = '\t')
anat_dir = f'{gl.baseDir}/anatomicals'


mask_paths = []

for i in range(0, p_df.shape[0]):
    p_id = p_df['ID'].iloc[i]
    week = (p_df['Week'].iloc[i]).strip() # sometimes have extra white spaces
    p_centre = (str(p_df['Centre'].iloc[i])).strip()

    subj_id = f'{p_centre.strip()}_{p_id}'

    t1_path = f'{anat_dir}/{subj_id}/{week}/{subj_id}_{week}_T1.nii'

    if not Path(t1_path).is_file():
            print(f'T1 path does not exist for {subj_id} in week {week}')
            continue
    
    results_path = f'{anat_dir}/{subj_id}/{week}/'

    mask_paths.append(te.isolate(t1_path = t1_path,
               subj_id = subj_id,
               week = week,
               results_path = results_path
               ))

    print(f'Cerebellar isolation mask for {subj_id} at {week} done!')    