import numpy as np
import pandas as pd

import SUITPy as suit

from smarts_cerebellum.util import file_search

def _add_demographics(df, p_df, subj):
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
    refT1   = p_df[p_df.subj_id == subj]['RefT1'].iloc[0].strip()
    subj_df = p_df[(p_df.subj_id == subj) & (p_df.Week.str.strip() == refT1)]


    # mask the row to which we are adding data
    row_mask = (df.subj_id == subj)

    df.loc[row_mask, 'subj_id']        = subj
    df.loc[row_mask, 'ID']             = subj_df['ID'].values[0]
    df.loc[row_mask, 'Centre']         = subj_df['Centre'].values[0]
    df.loc[row_mask, 'RefT1']          = refT1
    df.loc[row_mask, 'age']            = subj_df['age'].values[0]
    df.loc[row_mask, 'Gender']         = subj_df.Gender.values[0]
    df.loc[row_mask, 'isPatient']      = subj_df.isPatient.values[0]
    df.loc[row_mask, 'LesionSide']     = subj_df.LesionSide.values[0]
    df.loc[row_mask, 'LesionLocation'] = subj_df.LesionLocation.values[0]
    df.loc[row_mask, 'handedness']     = subj_df.handedness.values[0]
 
    return df


# Make summarized dataframe
def make_dataframe_atlas_space(the_atlas     = None,
                                maps         = None,
                                space        = 'MNISym_coreg_reslice',
                                segment      = 'T1',
                                param        = 'slope',
                                label_image  = None,
                                region_names = None,
                              ):

    dfs = []

    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'))

    subj_ids = p_df.subj_id
    LesionSide = p_df.LesionSide

    # loop through all subjects - perform each operation on each subject
    for subj, ls in zip(subj_ids, LesionSide):
        # find their files - returns string list of files

        if ls == 'left':
            img = nb.load(os.path.join(gl.baseDir, 'Regression', f'{subj}_{space}_{segment}_{param}_FlipLR.nii'))
        else:
            img = nb.load(os.path.join(gl.baseDir, 'Regression', f'{subj}_{space}_{segment}_{param}.nii'))
        
        # summarize volume in each ROI for each file type
        suit.fetch_atlas(the_atlas)
        df = suit.summarize_data(images = img,
                                 atlas = the_atlas,
                                 maps = maps,
                                 space = space,
                                 stats = ['mean', 'median', 'nansum'],
                                 label_image = label_image,
                                 region_names = region_names)
        

        # then make the descriptive dataframe for each subject
        df = _add_demographics(df, p_df, subj)

        # add all dataframes to the list
        dfs.append(df)

    # combine all of them
    all_df = pd.concat(dfs, ignore_index = True)

    return all_df
