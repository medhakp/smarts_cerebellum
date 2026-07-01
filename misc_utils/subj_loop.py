"""
ADD THIS TO HELPER FUNCTIONS FOLDER?
Use: (primarily as a helper function) for looping through all subjects in a participants info file.
"""
import pandas as pd
from pathlib import Path


tissue_dict = {
    'gm': 'c1',
    'wm': 'c2',
    'csf': 'c3'
}

def subj_loop(participants_df, # information tsv as filename or path
              # FIX: OPTION TO INPUT TSV, CSV, ETC (CHOOSE FILE TYPE), OR DIRECTLY AS PANDAS DATAFRAME
              anat_dir, # directory with anatomicals (for example)
              tissue # fix: option to not have tissue
              ):
    p_df = pd.read_csv(participants_df, sep = '\t')
    for i in range(0, p_df.shape[0]):
        p_id = p_df['ID'].iloc[i]
        week = (p_df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(p_df['Centre'].iloc[i])).strip()
        refT1 = (p_df['RefT1'].iloc[i]).strip()

        subj_id = f'{p_centre.strip()}_{p_id}'

        t1_path = f'{anat_dir}/{subj_id}/{week}/{subj_id}_{week}_T1.nii'
        tissue_path = f'{anat_dir}/{subj_id}/{week}/{tissue_dict[tissue]}{subj_id}_{week}_T1.nii'

        # check that paths exist
        if not Path(t1_path).is_file():
            print(f'T1 path does not exist for {subj_id} in week {week}')
            continue
        if not Path(tissue_path).is_file():
            print(f'{tissue} path does not exist for {subj_id} in week {week}')
            continue

    return (p_id, week, p_centre, refT1, subj_id, t1_path, tissue_path)