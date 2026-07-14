import numpy as np
import pandas as pd

import SUITPy as suit

from smarts_cerebellum.util import file_search

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
    
    # for subj_unique, so only take the reference week's descriptive information (all the same)
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



def _use_flipped(subj, search_path, flip, flip_lesion_df, suffixes, flipped_suffixes):
    """
    Determines whether to use flipped files; returns list of files for each subject (flipped files or regular files)
    """
    if flip != 'false':
            

            if subj in flip_lesion_df.subj_id.unique():
                file_list = file_search(search_path = search_path, subj_id = subj, suffixes = flipped_suffixes)
            else: # use not-flipped files for all others - this works on non-patients as well
                file_list = file_search(search_path = search_path, subj_id = subj, suffixes = suffixes)
    else:
        file_list = file_search(search_path = search_path, subj_id = subj, suffixes = suffixes)

    return file_list




# Make summarized dataframe
def make_summarized_dataframe(p_df,
                              search_path,
                              the_atlas, 
                              maps, 
                              space,
                              suffixes,
                              flip,
                              flipped_suffixes = None,
                              label_image = None,
                              region_names = None,
                              #use_weeks = False, # if using subject weeks, set True                              
                              ):
    """
    Make full summarized dataframe that has: ROIs for each subject, along with descriptive information

    Inputs:
        p_df (Pandas dataframe): info file for participants
        search_path (str): directory where files are stored (parent directory for all subjects)

        the_atlas (str): cerebellar atlas --> see SUITPy
        maps (str): map to use in summarizing (cerebellar map) --> see SUITPy
        space: space of the files

        suffixes (tuple of str): suffixes for all files you want to find
        flipped_suffixes (tuple of str): None by default; suffixes for flipped files
            ONLY used if flip is not None

        flip (str): flip lesion
            'false': don't flip
            left: flip lesions on left hemisphere to the right hemisphere
        
        #use_weeks (bool): if using subject weeks
            maybe make two separate functions, one for subject_unqiue and one for subject_weeks?


    Outputs:

    """

    dfs = []

    if flip == 'left':
        # need to strip bc sometimes have whitespaces - get rid of those
        flip_lesion_df = p_df[p_df.LesionSide.str.strip() == 'left']

    # if use_weeks:
    #     for subj, week in _subj_week_loop

    # loop through all subjects - perform each operation on each subject
    for subj in p_df.subj_id.unique():
        # find their files - returns string list of files

        # if need to flip lesions, find the flipped files
        file_list = _use_flipped(subj = subj, search_path = search_path, flip = flip, 
                                 flip_lesion_df = flip_lesion_df, 
                                 suffixes = suffixes, flipped_suffixes = flipped_suffixes)
       
        
        if not file_list:
            continue # skip subjects without the files
        
        # summarize volume in each ROI for each file type
        suit.fetch_atlas(the_atlas)
        df = suit.summarize_data(images = file_list,
                                 atlas = the_atlas,
                                 maps = maps,
                                 space = space,
                                 stats = ['mean', 'median', 'nansum'],
                                 label_image = label_image,
                                 region_names = region_names)
        
        df['subj_id']= subj

        # then make the descriptive dataframe for each subject
        descriptive_df = _assemble_dataframe(atlas_df = df, p_df = p_df, subj = subj)

        # add all dataframes to the list
        dfs.append(descriptive_df)

    # combine all of them
    all_df = pd.concat(dfs, ignore_index = True)

    return all_df
