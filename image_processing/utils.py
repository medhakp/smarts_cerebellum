import numpy as np
import pandas as pd
from pathlib import Path

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