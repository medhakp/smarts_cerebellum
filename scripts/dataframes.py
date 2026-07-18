import pandas as pd
import SUITPy as suit
import smarts_cerebellum.globals as gl
import nibabel as nb
import os

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


def _load_img_list(p_df, folder, subj, space, segment, param):

    p_df_s = p_df[p_df.subj_id==subj]

    LesionSide = p_df_s.LesionSide.unique()
        
    imgs = []
    if p_df_s.shape[0] > 1:
        weeks = p_df_s.Week.unique()
        for _week in weeks:
            week = _week.astype(str).strip()
            if LesionSide == 'left ':
                fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}_{param}_FlipLR.nii.gz')
            else:
                fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}_{param}.nii.gz')
            
            if os.path.isfile(fname):
                imgs.append(nb.load(fname))
    else:
        if LesionSide == 'left ':
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{space}_{segment}_{param}_FlipLR.nii.gz')
        else:
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{space}_{segment}_{param}.nii.gz')
        
        if os.path.isfile(fname):
            imgs.append(nb.load(fname))

    return imgs


# Make summarized dataframe 
def make_dataframe_atlas_space(
                                p_df         = None,
                                the_atlas    = None,
                                maps         = None,
                                folder       = None,
                                space        = 'MNISym',
                                segment      = 'T1',
                                param        = 'slope',
                                label_image  = None,
                                region_names = None,
                              ):

    dfs = []

    subj_ids = p_df.subj_id

    # loop through all subjects - perform each operation on each subject
    for subj in subj_ids:
        
        imgs = _load_img_list(p_df, folder, subj, space, segment, param)
        if len(imgs)==0:
            continue
        
        # summarize volume in each ROI for each file type
        suit.fetch_atlas(the_atlas) if the_atlas is not None else None
        df_subj = suit.summarize_data(images = imgs,
                                        atlas = the_atlas,
                                        maps = maps,
                                        space = space,
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

    df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{segment}_{param}.tsv'), sep='\t', index=False)


if __name__=='__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    p_df_w0 = p_df.sort_values("Week").groupby("subj_id", as_index=False).first()
    label_image=os.path.join(gl.baseDir, 'ROI', 'MNISymC.CST.nii')
    segments = ['T1', 'WM', 'GM', 'CSF']
    for segment in segments:
        make_dataframe_atlas_space(
            p_df=p_df_w0,
            folder = 'Regression',
            segment = segment,
            param = 'slope',
            label_image=label_image,
            region_names=[''] * 13 + ['left_CST', 'right_CST']
        )