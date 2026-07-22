import pandas as pd
import numpy as np
import re
from pathlib import Path
import nibabel as nib
import smarts_cerebellum.globals as gl


def tract_df(df, tract = 'CST'):
    # cut dataframe: patients left, right; controls bilateral tract (e.g. CST)
    patients = df[df.isPatient == 1]
    controls = df[df.isPatient == 0]

    r_patients = np.array(df[(df.isPatient == 1) & (df.regionname == f'right_{tract}')]['mean'])
    l_patients = np.array(df[(df.isPatient == 1) & (df.regionname == f'left_{tract}')]['mean'])
    
    controls_bilat = controls.groupby('subj_id').agg({'mean': 'mean'}).reset_index()
    controls_bilat['regionname'] = f'bilat_{tract}'
    controls_bilat['isPatient'] = 0
    
    b_controls = np.array(controls_bilat['mean'])
    patients_lr = patients[patients.regionname.isin([f'left_{tract}', f'right_{tract}'])]
    tract_df = pd.concat([patients_lr, controls_bilat], ignore_index=True)

    return r_patients, l_patients, b_controls, tract_df




def find_subjects(week, df):
    """
    Finds all subjects with data for a given week (int)

    Put in your own df, in case you wanted something like just patients
    """
        
    # get only that week's dataframe
    df_week = df[df.week == week]
    subjects = []
    for subj in df_week.subj_id:
        subjects.append(subj)
    return subjects

def subj_path_search(reference_file, ref_subj_id, week, df):
    """
    Given a reference file (path) and a reference subject id:
    looks in the path for that ref_subj_id and replaces it with other subj_id
    """

    ref_path = str(reference_file)

    if ref_subj_id not in ref_path:
        print(f"Subject token {ref_subj_id} not found in ref path, {ref_path}")
        return None
    
    # subject paths and subjects available for a given week
    subj_paths = []
    subj_available = []
    subjects = find_subjects(week, df)

    for subj_id in subjects:
        # replace subj_id token
        subj_path = re.sub(re.escape(ref_subj_id), subj_id, ref_path)

        if not Path(subj_path).exists():
            continue

        subj_paths.append(subj_path)
        subj_available.append(subj_id)

    return subj_paths, subj_available