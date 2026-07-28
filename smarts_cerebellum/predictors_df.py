import pandas as pd
import nibabel as nib
import os
import re
import SUITPy as suit
import smarts_cerebellum.globals as gl


def _week_token(image_name):
    match = re.search(r'W(\d+)', image_name)
    week_val = match.group(1)
    return week_val

def _load_img_list(p_df, folder, subj, space, segment):

    p_df_s = p_df[p_df.subj_id==subj]

    LesionSide = p_df_s.LesionSide.unique()
        
    imgs = []
    weeks = p_df_s.Week.unique()
    for _week in weeks:
        week = _week.strip()
        if LesionSide == 'left ':
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}_FlipLR.nii.gz')

        else:
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}.nii.gz')
        
        if os.path.isfile(fname):
            imgs.append(fname)

    return imgs

def response_df(p_df,
                     folder = None,
                     space = 'MNISymC',
                     atlas_space = 'MNISymC', # if using atlas and maps, set MNISym, etc.
                     segment = 'T1',
                     stats = ['mean'],
                     label_image = None,
                     region_names = None,
                     atlas = None,
                     maps = None,
                     ):
    dfs = []

    subj_ids = p_df.subj_id.unique()
    # find subj-week images - _load_img_list does this
    for subj in subj_ids:
        imgs = _load_img_list(p_df, folder, subj, space, segment)
        if len(imgs) == 0:
            continue
        if not atlas == None:
            suit.fetch_atlas(atlas)
        df_subj = suit.summarize_data(images = imgs,
                                      space = atlas_space,
                                      stats = stats,
                                      atlas = atlas,
                                      maps = maps,
                                      label_image = label_image,
                                      region_names = region_names)
        df_subj['subj_id'] = subj
        dfs.append(df_subj)
    
    df = pd.concat(dfs, ignore_index = True)
    df = df[~df.subj_id.isin(gl.bad)]
    df['Week'] = df['image_name'].apply(_week_token) # weeks in image name
    
    return df

    # save or return df? For now, we can just return it - we don't need to save it for now
    # so this is a general module; for our roi means, we can call it in the script, and pass this dataframe to our lme run