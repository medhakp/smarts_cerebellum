import pandas as pd
import SUITPy as suit
import smarts_cerebellum.globals as gl
import os
import re

def _week_token(image_name):
    match = re.search(r'W(\d+)', image_name)
    week_val = match.group(1)
    return week_val

def _add_demographics(df, p_df, subj):
    """

    Inputs:
        atlas_df (Pandas dataframe): dataframe from atlas summary
        p_info (Pandas dataframe): dataframe with descriptive information for participants

    Outputs:
        atlas_df (Pandas dataframe): updated dataframe (with descriptive information)
    """

    # for subj_unique, so only take the reference week's descriptive information (all the same)

    subj_df = p_df[p_df.subj_id == subj]
    refT1   = subj_df.RefT1.iloc[0].strip()
    Week    = subj_df.Week

    df['Week']           = Week
    df['subj_id']        = subj
    df['ID']             = subj_df['ID'].values[0]
    df['Centre']         = subj_df['Centre'].values[0]
    df['RefT1']          = refT1
    df['age']            = subj_df['age'].values[0]
    df['Gender']         = subj_df.Gender.values[0]
    df['isPatient']      = subj_df.isPatient.values[0]
    df['LesionSide']     = subj_df.LesionSide.values[0]
    df['LesionLocation'] = subj_df.LesionLocation.values[0]
    df['handedness']     = subj_df.handedness.values[0]
 
    return df


def _load_img_list(p_df, folder, subj, space, segment, param, use_weeks):

    p_df_s = p_df[p_df.subj_id==subj]

    LesionSide = p_df_s.LesionSide.unique()
        
    imgs = []
    if use_weeks:
        weeks = p_df_s.Week.unique()
        for _week in weeks:
            week = _week.strip()
            if LesionSide == 'left ':
                fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}{param}_FlipLR.nii.gz')
            else:
                fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}{param}.nii.gz')
            
            if os.path.isfile(fname):
                imgs.append(fname)
    else:
        if LesionSide == 'left ':
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{space}_{segment}{param}_FlipLR.nii.gz')
        else:
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{space}_{segment}{param}.nii.gz')
        
        if os.path.isfile(fname):
            imgs.append(fname)
    return imgs

# Make summarized dataframe 
def make_dataframe_atlas_space(
                                p_df         = None,
                                use_weeks = False,
                                the_atlas    = None,
                                maps         = None,
                                folder       = None,
                                space        = 'MNISymC',
                                atlas_space = 'MNISym',
                                segment      = 'T1',
                                param        = '_slope',
                                label_image  = None,
                                region_names = None,
                                rois = None
                              ):

    dfs = []

    subj_ids = p_df.subj_id.unique()

    # loop through all subjects - perform each operation on each subject
    for subj in subj_ids:
        
        imgs = _load_img_list(p_df, folder, subj, space, segment, param, use_weeks)
        if len(imgs)==0:
            continue
        
        # summarize volume in each ROI for each file type
        suit.fetch_atlas(the_atlas) if the_atlas is not None else None
        df_subj = suit.summarize_data(images = imgs,
                                        atlas = the_atlas,
                                        maps = maps,
                                        space = atlas_space,
                                        stats = ['mean'],
                                        label_image = label_image,
                                        region_names = region_names)
        

        # then make the descriptive dataframe for each subject
        df_subj = _add_demographics(df_subj, p_df, subj)

        # add all dataframes to the list
        dfs.append(df_subj)

    # combine all of them
    df = pd.concat(dfs, ignore_index = True)
    df = df[~df.subj_id.isin(gl.bad)]

    if use_weeks:
        df['Week'] = df['image_name'].apply(_week_token)

    df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{rois}_{segment}{param}.tsv'), sep='\t', index=False)

if __name__=='__main__':
    #REGRESSION SLOPE DATAFRAMES
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    p_df_w0 = p_df.sort_values("Week").groupby("subj_id", as_index=False).first()
    
    space = 'MNISymC'
    segments = ['T1', 'WM_mod', 'GM_mod', 'CSF_mod']
    folders = [f'{space}_T1', f'{space}_WM', f'{space}_GM', f'{space}_CSF']

    # atlas
    the_atlas = 'Nettekoven_2024'
    maps = 'atl-NettekovenSym32'

    for segment, folder in zip(segments, folders):
        make_dataframe_atlas_space(
            p_df=p_df_w0,
            folder = 'regression',
            segment = segment,
            param = '_slope',
            the_atlas = the_atlas,
            maps = maps,
            rois = the_atlas
        )
