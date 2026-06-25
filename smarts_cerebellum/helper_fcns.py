# DEPRECATED
# THIS IS UTILS

import pandas as pd
import re
from pathlib import Path

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