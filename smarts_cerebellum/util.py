"""
This utils file contains helper functions that are used by functions in smarts_cerebellum.
"""

import pandas as pd
import re
from pathlib import Path
import nibabel as nib


# this function can just do the subject-week loop and return subj_id, week
def subj_week_loop(df):
    for i in range(0, df.shape[0]):
        p_id = df['ID'].iloc[i]
        week = (df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(df['Centre'].iloc[i])).strip()
        subj_id = f'{p_centre.strip()}_{p_id}'

        # return each subj_id, week one at a time
        yield subj_id, week



#___________________________________________________________________________________
def find_weeks(SID):

    # @Marco
    
    ### look into particpants.tsv and return weeks as numpy array of int e.g., (2, 4, )
    
    p_df = pd.read_csv('/cifs/diedrichsen/data/smarts_cerebellum/participants_anat.tsv', sep = '\t')

    # access only that subject's rows
    df_subj = p_df[p_df.subj_id == SID]
    weeks = []

    for week in df_subj['week']:
        weeks.append(week)

    return weeks


def week_path_search(reference_file, subj_id):
    """
    Finds files from other weeks that match the structure of reference file.

    Inputs:
        reference_file (str): path to a file whose path will be used as reference.
            That is, this file's path should have the structure that all other files from that week should have.
        weeks: weeks in filepath
    
    Outputs:
        week_paths (list[str]): paths to all files (including reference) that exist for weeks
        week_available (list[str]): weeks whose files exist
    """

    ref_path = str(reference_file)

    # find all places in path str with the week
    match = re.search(r'W(\d+)', ref_path)
    if not match:
        print(f'could not find week token in reference path for {ref_path}')
        return None
    
    ref_week_token = match.group(1) # return entire text that ws matched.

    weeks_paths = []
    weeks_available = []

    weeks = find_weeks(subj_id)

    for week in weeks:
        # search for every week's file

        # replace the week token(s) in reference image path with other tokens for new week path
        #week_path = ref_path.replace(ref_week_token, f'W{week}')

        week_path = re.sub(rf'W{ref_week_token}(?!\d)', f'W{week}', ref_path)

        # this should be dead code
        if not Path(week_path).exists():
            print(f'skipping W{week}')
            continue

        weeks_paths.append(week_path)
        weeks_available.append(week) # add weeks as integers

    return weeks_paths, weeks_available

def file_search(search_path, subj_id, suffixes):
    """
    Function to search for all files for a given subject with specified suffixes.
    Also checks if files exist - only returns those that exist.

    Inputs:
        search_path (str): base path to search for files in
        subj_id (str): subject whose file(s) to search for - searches in their directory
        suffixes (tuple of str): suffixes of files; include extension (i.e. .nii or .nii.gz extensions)
        # (TBA) week (str): if subject files are stored by weeks
    
    Outputs:
        file_list (tuple of str): list of files for that subject
    """

    file_list = []

    for suffix in suffixes:
        file_path = f'{search_path}/{subj_id}/{subj_id}_{suffix}'

        if not Path(file_path).is_file():
            #print(f'Path {file_path} not found; skipping')
            continue

        file_list.append(file_path)
    
    return file_list



def file_search_weeks(search_path, subj_id, week, suffixes):
    """
    Function to search for all files for a given subject-week with specified suffixes.
    Also checks if files exist - only returns those that exist.

    Inputs:
        search_path (str): base path to search for files in
        subj_id (str): subject whose file(s) to search for - searches in their directory
        week (str): subject's week to search in
        suffixes (tuple of str): suffixes of files; include extension (i.e. .nii or .nii.gz extensions)
        # (TBA) week (str): if subject files are stored by weeks
    
    Outputs:
        file_list (tuple of str): list of files for that subject-week
    """

    file_list = []

    for suffix in suffixes:
        file_path = f'{search_path}/{subj_id}/{subj_id}_{week}_{suffix}'

        if not Path(file_path).is_file():
            #print(f'Path {file_path} not found; skipping')
            continue

        file_list.append(file_path)
    
    return file_list
    
#___________________________________________________________________________________

"""
subj_search functions: functions to search for files across different subjects (within the same week)
"""
#___________________________________________________________________________________
def find_subjects(week):
    """
    Finds all subjects with data for a given week (int)
    """
    p_df = pd.read_csv(f'{gl.baseDir}/participants_anat.tsv', sep = '\t')
    
    # get only that week's dataframe
    df_week = p_df[p_df.week == week]
    subjects = []
    for subj in df_week.subj_id:
        subjects.append(subj)
    return subjects

def subj_path_search(reference_file, ref_subj_id, week):
    """
    Given a reference file (path) and a reference subject id:
    looks in the path for that ref_subj_id and replaces it with other subj_id

    NOTE:
    
    make sure to use this function correctly: put subj = 'subj_id', week = INT.

    In search_path, do it like `MNISym_T1/{subj}/{subj}_W{week}_MNISym_T1_coreg_reslice.nii.gz'

    EXAMPLE CALL:
    subj = 'CU_2310'
    week = 24
    search_path = f'{gl.baseDir}/MNISym_T1/{subj}/{subj}_W{week}_MNISym_T1_coreg_reslice.nii.gz'
    subj_paths, subj_available = subj_path_search(search_path, subj, week)
    """

    ref_path = str(reference_file)

    if ref_subj_id not in ref_path:
        print(f"Subject token {ref_subj_id} not found in ref path, {ref_path}")
        return None
    
    # subject paths and subjects available for a given week
    subj_paths = []
    subj_available = []
    subjects = find_subjects(week)

    for subj_id in subjects:
        # replace subj_id token
        subj_path = re.sub(re.escape(ref_subj_id), subj_id, ref_path)

        if not Path(subj_path).exists():
            print(subj_path)
            #print(f'skipped {subj_id} {week}')
            continue

        subj_paths.append(subj_path)
        subj_available.append(subj_id)

    return subj_paths, subj_available
#___________________________________________________________________________________