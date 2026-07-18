import numpy as np
import pandas as pd

import SUITPy as suit

from smarts_cerebellum.util import file_search_weeks, subj_week_loop

def _assemble_dataframe(atlas_df, p_df, subj, week):
    """
    Creates a descriptive dataframe
    UNIQUE SUBJECT IMAGE, NOT WEEKS! --> weeks under construction!

    Inputs:
        atlas_df (Pandas dataframe): dataframe from atlas summary
        p_info (Pandas dataframe): dataframe with descriptive information for participants

    Outputs:
        atlas_df (Pandas dataframe): updated dataframe (with descriptive information)
    """
    
    refT1 = p_df[p_df.subj_id == subj]['RefT1'].iloc[0].strip()
    subj_df=p_df[(p_df.subj_id == subj) & (p_df.Week.str.strip() == week)] # W0, W4, ...


    # mask the row to which we are adding data
    row_mask = (atlas_df.subj_id == subj)
    print(f'Writing data for {subj}')

    atlas_df.loc[row_mask, 'ID'] = subj_df['ID'].values[0]
    atlas_df.loc[row_mask, 'Centre'] = subj_df['Centre'].values[0]
    atlas_df.loc[row_mask, 'RefT1'] = refT1
    atlas_df.loc[row_mask, 'Week'] = week
    atlas_df.loc[row_mask, 'week'] = subj_df['week'].values[0]
    atlas_df.loc[row_mask, 'age'] = subj_df['age'].values[0]
    atlas_df.loc[row_mask, 'Gender'] = subj_df.Gender.values[0]
    atlas_df.loc[row_mask, 'isPatient'] = subj_df.isPatient.values[0]
    atlas_df.loc[row_mask, 'LesionSide'] = subj_df.LesionSide.values[0]
    atlas_df.loc[row_mask, 'LesionLocation'] = subj_df.LesionLocation.values[0]
    atlas_df.loc[row_mask, 'handedness'] = subj_df.handedness.values[0]
 
    return atlas_df


def _get_files(subj, week, search_path, suffixes):
    """
    Returns all subject-week files
    """
    file_list = file_search_weeks(search_path = search_path, subj_id = subj, week = week, suffixes = suffixes)
    return file_list



# Make summarized dataframe
def make_summarized_dataframe_weeks(p_df,
                              search_path,
                              the_atlas=None, 
                              maps=None, 
                              space='MNISym',
                              suffixes = None,
 
                              ):
    """
    Make full summarized dataframe that has: ROIs for each subject, along with descriptive information
    Used for subject-weeks.

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

   

    # loop through all subjects - perform each operation on each subject
    for subj, week in subj_week_loop(df=p_df):
        # find their files - returns string list of files

        # if need to flip lesions, find the flipped files
        file_list = _get_files(subj = subj, search_path = search_path, week = week, suffixes = suffixes, )
       
        
        if not file_list:
            print(subj)
            continue # skip subjects without the files
        print(file_list)
        # summarize volume in each ROI for each file type
        suit.fetch_atlas(the_atlas)
        df = suit.summarize_data(images = file_list,
                                 atlas = the_atlas,
                                 maps = maps,
                                 space = space,
                                 stats = ['mean', 'median', 'nansum'])
        
        df['subj_id']= subj

        # then make the descriptive dataframe for each subject
        descriptive_df = _assemble_dataframe(atlas_df = df, p_df = p_df, subj = subj, week = week)

        # add all dataframes to the list
        dfs.append(descriptive_df)

    # combine all of them
    all_df = pd.concat(dfs, ignore_index = True)

    return all_df
