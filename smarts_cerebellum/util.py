import numpy as np
import pandas as pd

import re
import nibabel as nib
from pathlib import Path
import SUITPy as suit


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


def _assemble_dataframe(atlas_df, p_df, subj):
    """
    Creates a descriptive dataframe
    UNIQUE SUBJECT IMAGE, NOT WEEKS! --> weeks under construction!

    Inputs:
        atlas_df (Pandas dataframe): dataframe from atlas summary
        p_info (Pandas dataframe): dataframe with descriptive information for participants

    Outputs:
        atlas_df (Pandas dataframe): updated dataframe (with descriptive information)
    """

    # try doing this for only one subject; then, we can loop through in the call
    refT1 = p_df[p_df.subj_id == subj]['RefT1'].iloc[0].strip()
    subj_df = p_df[(p_df.subj_id == subj) & (p_df.Week.str.strip() == refT1)]


    # mask the row to which we are adding data
    row_mask = (atlas_df.subj_id == subj)
    print(f'Writing data for {subj}')

    atlas_df.loc[row_mask, 'ID'] = subj_df['ID'].values[0]
    atlas_df.loc[row_mask, 'Centre'] = subj_df['Centre'].values[0]
    atlas_df.loc[row_mask, 'RefT1'] = refT1
    atlas_df.loc[row_mask, 'age'] = subj_df['age'].values[0]
    atlas_df.loc[row_mask, 'Gender'] = subj_df.Gender.values[0]
    atlas_df.loc[row_mask, 'isPatient'] = subj_df.isPatient.values[0]
    atlas_df.loc[row_mask, 'LesionSide'] = subj_df.LesionSide.values[0]
    atlas_df.loc[row_mask, 'LesionLocation'] = subj_df.LesionLocation.values[0]
    atlas_df.loc[row_mask, 'handedness'] = subj_df.handedness.values[0]
 
    return atlas_df


# Make summarized dataframe
def make_summarized_dataframe(p_df,
                              search_path,
                              the_atlas, maps, space,
                              ):
    """
    Make full summarized dataframe that has: ROIs for each subject, along with descriptive information

    Inputs:
        p_df (Pandas dataframe): info file for participants
        search_path (str): directory where files are stored (parent directory for all subjects)
        suffixes (tuple of str): suffixes for all files you want to find

        the_atlas (str): cerebellar atlas --> see SUITPy
        maps (str): map to use in summarizing (cerebellar map) --> see SUITPy
        space: space of the files


    Outputs:

    """

    suffixes = [
    'MNISym_CSF_coreg_reslice_slope.nii.gz',
    'MNISym_logJac_coreg_reslice_slope.nii.gz',
    'MNISym_WM_coreg_reslice_slope.nii.gz',
    'MNISym_GM_coreg_reslice_slope.nii.gz',
    'MNISym_T1_coreg_reslice_slope.nii.gz'
    ]

    flipped_suffixes = [
        'MNISym_CSF_coreg_reslice_slope_FlipLR.nii.gz',
        'MNISym_logJac_coreg_reslice_slope_FlipLR.nii.gz',
        'MNISym_WM_coreg_reslice_slope_FlipLR.nii.gz',
        'MNISym_GM_coreg_reslice_slope_FlipLR.nii.gz',
        'MNISym_T1_coreg_reslice_slope_FlipLR.nii.gz'
    ]

    dfs = []

    left_lesion_df = p_df[p_df.LesionSide == 'left ']

    # loop through all subjects - perform each operation on each subject
    for subj in p_df.subj_id.unique():
        # find their files - returns string list of files
        if subj in left_lesion_df.subj_id.unique():
            file_list = file_search(search_path = search_path, subj_id = subj, suffixes = flipped_suffixes)
        else:
            file_list = file_search(search_path = search_path, subj_id = subj, suffixes = suffixes)
        
        if not file_list:
            continue # skip subjects without the files
        
        # summarize volume in each ROI for each file type
        suit.fetch_atlas(the_atlas)
        df = suit.summarize_data(images = file_list,
                                 atlas = the_atlas,
                                 maps = maps,
                                 space = space,
                                 stats = ['mean', 'median', 'nansum'])
        
        df['subj_id']= subj

        # then make the descriptive dataframe for each subject
        descriptive_df = _assemble_dataframe(atlas_df = df, p_df = p_df, subj = subj)

        # add all dataframes to the list
        dfs.append(descriptive_df)

    # combine all of them
    all_df = pd.concat(dfs, ignore_index = True)

    return all_df


def flip_left_lesion(path, left_lesion_df, suffix):
    '''
    flip left lesion to the right
    
    Inputs:
        path (str): base path to subject files
        left_lesion_df (Pandas dataframe): dataframe containing all participants with left hemisphere lesion - to be flipped!
        suffix (str): image suffix (for image to be flipped)

        Filenames follow convention {subj}_{suffix}.nii.gz
        Output images saved as {subj}_{suffix}_FlipLR.nii.gz
        File path follows convention {path}/{subj}/{file_name}
    '''

    def _FlipLR(image):
        """
        Simple flip: flips image along x-axis (L-R flip)

        Input: image (Nifti or string)

        Output: Nifti image
        """
        if type(image) == str:
            image = nib.load(image)
        
        img_arr = image.get_fdata()

        flip_LR = img_arr[::-1, :,:]

        flipped_img = nib.Nifti1Image(flip_LR, image.affine)
        
        return flipped_img


    for subj in left_lesion_df.subj_id.unique():
        flip = f'{path}/{subj}/{subj}_{suffix}.nii.gz'
        if not Path(flip).is_file():
            print(f'Skip {subj}')
            continue
        flipped = _FlipLR(flip)
        nib.save(flipped, f'{path}/{subj}/{subj}_{suffix}_FlipLR.nii.gz')

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

    # find all places in path with the week
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