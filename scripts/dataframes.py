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


def _load_img_list(p_df, folder, subj, space, segment, param, use_weeks, use_flipped = True):

    p_df_s = p_df[p_df.subj_id==subj]

    LesionSide = p_df_s.LesionSide.unique()
        
    imgs = []
    if use_weeks:
        weeks = p_df_s.Week.unique()
        for _week in weeks:
            week = _week.strip()
            if LesionSide == 'left ' & use_flipped == True:
                fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}{param}_FlipLR.nii.gz')
            else:
                fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}{param}.nii.gz')
            
            if os.path.isfile(fname):
                imgs.append(fname)
    else:
        if LesionSide == 'left ' & use_flipped == True:
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{space}_{segment}{param}_FlipLR.nii.gz')
        else:
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{space}_{segment}{param}.nii.gz')
        
        if os.path.isfile(fname):
            imgs.append(fname)
    return imgs

def _atlas_loop(subj_ids,
                p_df,
                folder,
                space,
                atlas_space,
                the_atlas,
                maps,
                label_image,
                region_names,
                segment,
                param,
                use_weeks):
    dfs = []

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
    return dfs
    
def _subj_week_atlas_loop(subj_ids,
                            p_df,
                            folder,
                            space,
                            atlas_space,
                            maps,
                            segment,
                            param):
    dfs = []
    # also find subj-week atlases
    for subj in subj_ids:
        
        # get subj-week atlas
        atlas_imgs = _load_img_list(p_df, folder, subj, space = f'{maps}_space-{atlas_space}', segment = segment, param = 'dseg', use_weeks=True, use_flipped = False)
                # function looks for name: {subj}_{week}_{space}_{segment}{param}.nii.gz
                # atlas names: atl-NettekovenSym32_space-MNISym_dseg.nii
                # our files will be named: {subj}_{week}_{space = {maps}_space-{atlas_space}}_{param = dseg}.nii.gz} # (must add .dseg)
                # so space = {maps}_space-{space}; param = dseg
        if len(atlas_imgs) == 0:
            continue

        # get subj-week images
        imgs = _load_img_list(p_df, folder, subj, space, segment, param, use_weeks = True)
        if len(imgs)==0:
            continue
        


        # summarize with custom label image - regionnames from lut - need to do this for each subj-week
        # so zip through subj-week atlases and subj-week images
        # lut: atl-NettekovenSym32.lut

        for atlas_img, img in zip(atlas_imgs, imgs):

            # make sure atlas_img, img are same week___
            atlas_week = _week_token(atlas_img)
            img_week = _week_token(img)
            if not atlas_week == img_week:
                print(f"week mismatch in {subj}: atlas = {atlas_week}, img = {img_week}")
                continue
            #______________

            df_subj_week = suit.summarize_data(images = img,
                                               space = atlas_space,
                                               stats = ['mean'],
                                               label_img = atlas_img,
                                               lut = f'{atlas_space}.lut')
            
            df_subj_week = _add_demographics(df_subj_week, p_df, subj)

            # add all dataframes to the list
            dfs.append(df_subj_week)
        
        return dfs

# Make summarized dataframe 
def make_dataframe_atlas_space(
                                p_df         = None,
                                use_weeks = None,
                                subj_week_atlas = False, # native space ROIs; 
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

    subj_ids = p_df.subj_id.unique()

    if subj_week_atlas == False:
        dfs = _atlas_loop(subj_ids,
                p_df,
                folder,
                space,
                atlas_space,
                the_atlas,
                maps,
                label_image,
                region_names,
                segment,
                param,
                use_weeks)
    else: # use subj-week specific atlases with specified atlas name (name = subj_week_ATLAS.nii.gz)
        dfs = _subj_week_atlas_loop(subj_ids,
                            p_df,
                            folder,
                            space,
                            atlas_space,
                            maps,
                            segment,
                            param)
        


    # combine all of them
    df = pd.concat(dfs, ignore_index = True)
    df = df[~df.subj_id.isin(gl.bad)]

    if use_weeks:
        df['Week'] = df['image_name'].apply(_week_token)

    df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{rois}_{segment}{param}.tsv'), sep='\t', index=False)

if __name__=='__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    #p_df_w0 = p_df.sort_values("Week").groupby("subj_id", as_index=False).first()

    space = 'MNISymC'
    segments = ['T1', 'WM_mod', 'GM_mod', 'CSF_mod']
    folders = [f'{space}_T1', f'{space}_WM', f'{space}_GM', f'{space}_CSF']


    # NORMALIZED (MOD TISSUE) IMAGES
    # custom label image
    roi_tract = 'CST'
    label_image=os.path.join(gl.baseDir, 'ROI', f'MNISymC.{roi_tract}.nii')
    region_names = [''] * 13 + [f'left_{roi_tract}', f'right_{roi_tract}']

    # atlas
    the_atlas = 'Nettekoven_2024'
    maps = 'atl-NettekovenSym32'


    for segment, folder in zip(segments, folders):
        make_dataframe_atlas_space(
            p_df=p_df,
            use_weeks = True,
            folder = folder,
            segment = segment,
            param = '',
            label_image=label_image,
            region_names = region_names,
            rois = roi_tract
        )

    for segment, folder in zip(segments, folders):
        make_dataframe_atlas_space(
            p_df=p_df,
            use_weeks = True,
            folder = folder,
            segment = segment,
            param = '',
            the_atlas = the_atlas,
            maps = maps,
            rois = the_atlas
        )


    # REGRESSION SLOPE DATAFRAMES
    # roi_tract = 'MCP'
    # label_image=os.path.join(gl.baseDir, 'ROI', f'MNISymC.{roi_tract}.nii')
    # segments = ['T1', 'WM_mod', 'GM_mod', 'CSF_mod']
    # for segment in segments:
    #     make_dataframe_atlas_space(
    #         p_df=p_df_w0,
    #         folder = 'regression',
    #         segment = segment,
    #         param = '_slope',
    #         label_image=label_image,
    #         region_names=[''] * 2 + [f'left_{roi_tract}', f'right_{roi_tract}'], # adjust label as needed; indexing starts from 1
    #         rois = roi_tract
    #     )