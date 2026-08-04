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
    

    subj_df = p_df[p_df.subj_id == subj]
    refT1   = subj_df.RefT1.iloc[0].strip()

    df['Week']           = df['image_name'].apply(_week_token)
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
            if LesionSide == 'left ' and use_flipped:
                fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}{param}_FlipLR.nii.gz') # subj/subj_week_file
                fname_else = os.path.join(gl.baseDir, folder, subj, week, f'{subj}_{week}_{space}_{segment}{param}_FlipLR.nii.gz') # subj/week/subj_week_file
                fname_anat = '' # anatomicals

            else:
                fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{week}_{space}_{segment}{param}.nii.gz')
                fname_else = os.path.join(gl.baseDir, folder, subj, week, f'{subj}_{week}_{space}_{segment}{param}.nii.gz')
                fname_anat = os.path.join(gl.baseDir, folder, subj, week, f'{subj}_{week}_T1.nii') # anatomicals
            
            if os.path.isfile(fname):
                imgs.append(fname)
            elif os.path.isfile(fname_else):
                imgs.append(fname_else)
            elif os.path.isfile(fname_anat):
                imgs.append(fname_anat)
    else:
        if LesionSide == 'left ' and use_flipped:
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{space}_{segment}{param}_FlipLR.nii.gz')
        else:
            fname = os.path.join(gl.baseDir, folder, subj, f'{subj}_{space}_{segment}{param}.nii.gz')
        
        if os.path.isfile(fname):
            imgs.append(fname)
    return imgs


    
def _subj_week_atlas_loop(subj_ids,
                            p_df,
                            folder,
                            space,
                            atlas_space,
                            maps,
                            segment,
                            param,
                            lut_file, 
                            region_names):
    dfs = []
    # also find subj-week atlases
    for subj in subj_ids:
        
        # get subj-week atlas
        atlas_imgs = _load_img_list(p_df, folder, subj, space = f'{maps}', segment = f'space-{atlas_space}', param = '_dseg', use_weeks=True, use_flipped = False)
                # function looks for name: {subj}_{week}_{space}_{segment}{param}.nii.gz
                # atlas names: atl-NettekovenSym32_space-MNISym_dseg.nii
                # our files will be named: {subj}_{week}_{space = {maps}_space-{atlas_space}}_{param = dseg}.nii.gz} # (must add .dseg)
                # so space = {maps}_space-{space}; param = dseg
        if len(atlas_imgs) == 0:
            continue

        # get subj-week images
        imgs = _load_img_list(p_df, folder, subj, space, segment, param, use_weeks = True, use_flipped = False)
        if len(imgs)==0:
            continue
        
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
                                               label_image = atlas_img,
                                               lut_file = lut_file)
            
            df_subj_week = _add_demographics(df_subj_week, p_df, subj)

            # add all dataframes to the list
            dfs.append(df_subj_week)
        
    return dfs

# Make summarized dataframe 
def make_dataframe_atlas_space(
                                p_df         = None,
                                use_weeks = None,
                                subj_week_atlas = True, # native space ROIs; 
                                the_atlas    = None,
                                maps         = None,
                                folder       = None,
                                space        = 'MNISymC',
                                atlas_space = 'MNISym',
                                segment      = 'T1',
                                param        = '_slope',
                                label_image  = None,
                                region_names = None,
                                rois = None,
                                lut_file = None # native ROIs
                              ):

    subj_ids = p_df.subj_id.unique()


    dfs = _subj_week_atlas_loop(subj_ids,
                        p_df,
                        folder,
                        space,
                        atlas_space,
                        maps,
                        segment,
                        param,
                        lut_file,
                        region_names = region_names)
        


    # combine all of them
    df = pd.concat(dfs, ignore_index = True)
    df = df[~df.subj_id.isin(gl.bad)]

    if use_weeks:
        df['Week'] = df['image_name'].apply(_week_token)

    df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{rois}_{segment}{param}.tsv'), sep='\t', index=False)

if __name__=='__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')

    space = ''
    #segments = ['T1', 'WM', 'GM', 'CSF']
    folder = 'anatomicals'
    the_atlas = 'Diedrichsen_2009'
    maps = 'atl-Anatom'
    lut_file = os.path.join(gl.baseDir, 'ROI', 'cerebellar_atlases', the_atlas, f'{maps}.lut') 
    segment = 'GM'
    
    make_dataframe_atlas_space(
        p_df = p_df,
        use_weeks = True,
        subj_week_atlas = True,
        the_atlas = the_atlas,
        maps = maps,
        folder = folder,
        atlas_space = 'MNISym',
        segment = segment,
        space = '',
        param = '',
        rois = the_atlas,
        lut_file = lut_file

        
    )
