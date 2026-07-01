# add project root
import sys
sys.path.append('/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/')

# Imports

import numpy as np

from pathlib import Path
import os

from helper_functions import parent_lookup

base_dir = '/cifs/diedrichsen/data/smarts_cerebellum'

def week_path_builder(reference_image, subj_id, subdir, suffix, tissue, week_folder):
    """
    Inputs:
        reference_image: in avg_vol
        subj_id: in avg_vol

        subdir: in avg_vol (NEED TO CHANGE NAME HERE)
        
        suffix: in avg_vol; DOCUMENTATION: NEED TO INCLUDE .NII OR .NII.GZ
        tissue: in avg_vol

        week_folder: need to add to avg_vol; boolean; whether files are stored within a weeks folder or just flat (then False)

    Output:
        week_path (str): path to file for that week
        weeks_available (list): weeks with available files (as W0, ..., etc.)
            This can be used in response_matrix() for avg_vol function

    ______________

    This function follows the naming convention:
        <tissue_segmentation><subj_id>_<week>_<suffix> 
            
            - tissue_segmentation: c1, ..., c5 (if segmentation file from SPM); if tissue = None, then that space is empty
            - suffix: see file_naming_conventions in README; end in .nii or .nii.gz
    """

    parent_path, level = parent_lookup.parent_lookup(file_path = reference_image, subj_id = subj_id)

    base_path = (Path(parent_path/subdir) if not subdir == None else parent_path)

    prefix = '' # empty string by default

    tissue_dict = {
    'gm': 'c1',
    'wm': 'c2',
    'csf': 'c3'
    }

    if not tissue == None:
        prefix = tissue_dict[tissue]
        print(tissue)

        # this part is the weeks loop___________________

    weeks = np.array([0,4,12,24,52])

    week_paths = []
    weeks_available = []

    for week in weeks:
        if week_folder == True:
            potential_path = f'{base_path}/W{week}/{prefix}{subj_id}_W{week}_{suffix}'
        else:
            potential_path = f'{base_path}/{prefix}{subj_id}_W{week}_{suffix}'

        # check if file exists
        if not os.path.exists(potential_path):
            print("skipping", subj_id, "W", week)
            continue

        # only return the path if it exists
        week_paths.append(potential_path)
        weeks_available.append('W' + week.astype(str))

    return week_paths, weeks_available