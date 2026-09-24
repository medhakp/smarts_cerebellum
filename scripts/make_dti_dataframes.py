import pandas as pd
import numpy as np
import io
import os
from pathlib import Path
import smarts_cerebellum.globals as gl

# use this to convert individual dataframes (subj-week dataframes) into a combined dataframe containing all subjs-weeks
# used for DTI dataframes

def _subj_week_loop(df):
    for i in range(0, df.shape[0]):
        p_id = df['ID'].iloc[i]
        week = (df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(df['Centre'].iloc[i])).strip()
        subj_id = f'{p_centre.strip()}_{p_id}'

        # return each subj_id, week one at a time
        yield subj_id, week



def subj_dti_df(subj_id, week):
    path = os.path.join(gl.baseDir, 'DTI', subj_id, week)
    file = 'JHU_MNI_SS_WMPM_TypeII_ver2.1_dti.txt'
    file_path = os.path.join(path, file)

    if not Path(file_path).exists():
        return None

    cols = ['Image', 'Object', 'Pixels', 'Min', 'Max', 'Mean', 'Std'] # columns to use

    # data lines start with "G:"; others are headers
    with open(file_path, "r", encoding = "utf-8") as f:
        data_lines = [line for line in f if line.startswith("G:")]

    df = pd.read_csv(io.StringIO("".join(data_lines)), sep = '\t', names = cols, usecols = range(7))
    df['metric'] = df['Image'].str.extract(r'\\([^\\]+)\.dat$') # get metric (from image name, using re method)
    df['subj_id'] = subj_id
    df['week'] = week
    df['Week'] = df['week'].str.extract(r'(\d+)') # get numeric values
    
    # rename columns to match convention used throughout this project
    df.rename(columns = {'Mean': 'mean', 'Object': 'regionname', 'Image': 'image_name'}, inplace = True)

    return df


def assign_side(df, p_df):
    """
    df = dataframe to assign side to
    p_df = reference dataframe (contains info)
    """
    # add lesion side - note that some patients with DTI are not in the anatomical p_df
    left_patients = p_df[p_df.LesionSide == 'left ']['subj_id'].unique()
    right_patients = p_df[p_df.LesionSide == 'right']['subj_id'].unique()
    #controls = p_df[p_df.LesionSide == 'none ']['subj_id'].unique()
    controls = p_df[p_df.Centre.str[-1] == 'P']['subj_id'].unique()
    df.loc[df.subj_id.isin(left_patients), 'LesionSide'] = 'left '
    df.loc[df.subj_id.isin(right_patients), 'LesionSide'] = 'right'
    df.loc[df.subj_id.isin(controls), 'LesionSide'] = 'none '
    
    df.loc[~df.subj_id.isin(controls), 'isPatient'] = 1
    df.loc[df.subj_id.isin(controls), 'isPatient'] = 0

    # given as: regionname_L (or regionname_R), but sometimes has region1_region2_L, etc.
    df['region_bilat'] = df.regionname.str.split('_').str[:-1].str.join('_')

    # all lesions flipped to the right
    df.loc[(df.isPatient == 1) & (df.regionname.str[-1] == 'L'), 'side'] = 'contralesional'
    df.loc[(df.isPatient == 1) & (df.regionname.str[-1] == 'R'), 'side'] = 'ipsilesional'

    return df

def flip_lesion_dti(df):
    """
    All lesions should be on the right side. So, finds those with left lesion, and "flips" the lesion by assigning left ROIs to right ROIs, and right ROIs to left ROIs.
    Analogous to image flipping done before.
    """
    dfs = []
    for subj in df.subj_id.unique():
        subj_df = df[df.subj_id == subj].copy()
        if subj_df.LesionSide.values[0] == 'left ':
            
            subj_df['regionname'] = subj_df['regionname'].str.replace(r'L$', 'T', regex = True) # need to add "regex = True"
            subj_df['regionname'] = subj_df['regionname'].str.replace(r'R$', 'L', regex = True)
            subj_df['regionname'] = subj_df['regionname'].str.replace(r'T$', 'R', regex = True)
            subj_df['is_flipped'] = 1 # lesion flipped
        else:
            subj_df['is_flipped'] = 0 # lesion not flipped
        
        dfs.append(subj_df)

    all_dfs = pd.concat(dfs, ignore_index = True)

    all_dfs['region_bilat'] = all_dfs['regionname'].str[:3]

    # all lesions flipped to the right - assign this correctly
    all_dfs.loc[(all_dfs.isPatient == 1) & (all_dfs.regionname.str[-1] == 'L'), 'side'] = 'contralesional'
    all_dfs.loc[(all_dfs.isPatient == 1) & (all_dfs.regionname.str[-1] == 'R'), 'side'] = 'ipsilesional'
    
    return all_dfs

def add_metrics(df):

    # rename eigenvalue rows (to follow convention for my sanity)
    df[df.metric == 'EgVal0'] = df[df.metric == 'EgVal0'].replace('EgVal0', 'lambda_1')
    df[df.metric == 'EgVal1'] = df[df.metric == 'EgVal1'].replace('EgVal1', 'lambda_2')
    df[df.metric == 'EgVal2'] = df[df.metric == 'EgVal2'].replace('EgVal2', 'lambda_3')


    # mean diffusivity (MD) = trace / 3
    md_rows = df[df.metric == 'trace'].copy().reset_index(drop = True)
    # we need to give it an arbitrary image name (for use in other functions (e.g. in lme_roi, _week_token())), so make name just the start of image_name, the part with subj, week; excluding metric.dat portion
    md_rows['image_name'] = md_rows['image_name'].str.extract(r'(.+?)' + md_rows.metric.iloc[0] + r'\.dat')[0]

    md_rows.metric = 'mean_diffusivity'
    md_rows['mean'] = md_rows['mean'] / 3

    # set other cols to nan, since we don't have it
    md_rows['Min'] = np.nan
    md_rows['Max'] = np.nan
    md_rows['Std'] = np.nan

    
    df = pd.concat([df, md_rows], ignore_index = True)

    # radial diffusivity (RD) = lambda_2 + lambda_3
    perpendiculars = ['lambda_2', 'lambda_3']
    perp_rows = df[df.metric.isin(perpendiculars)].copy().reset_index(drop = True)

    rd_rows = df[df.metric == 'trace'].copy().reset_index(drop = True) # just need the template of the dataframe to put new values in; metric == 'trace' is arbitrary here, just for df template purposes
    # we need to give it an arbitrary image name (for use in other functions (e.g. in lme_roi, _week_token())), so make name just the start of image_name, the part with subj, week; excluding metric.dat portion
    rd_rows['image_name'] = rd_rows['image_name'].str.extract(r'(.+?)' + rd_rows.metric.iloc[0] + r'\.dat')[0]

    rd_rows.metric = 'radial_diffusivity'
    

    lambda_2 = perp_rows[perp_rows.metric == 'lambda_2'].set_index(['subj_id', 'week', 'regionname'])['mean']
    lambda_3 = perp_rows[perp_rows.metric == 'lambda_3'].set_index(['subj_id', 'week', 'regionname'])['mean']

    rd_rows['mean'] = ((lambda_2 + lambda_3) /2).values

    # set other cols to nan, since we don't have it
    rd_rows['Min'] = np.nan
    rd_rows['Max'] = np.nan
    rd_rows['Std'] = np.nan


    df = pd.concat([df, rd_rows], ignore_index = True)

    return df

if __name__ == '__main__':
    p_dti = pd.read_excel(os.path.join(gl.baseDir, 'DTI', 'patient_list.xlsx'), usecols = range(10)) # only need the first 5 cols
    p_dti['subj_id'] = p_dti['Centre'].str.strip() + '_' + p_dti['ID'].astype(str)

    dfs = []

    for subj, week in _subj_week_loop(p_dti):
        df = subj_dti_df(subj, week)
        if df is not None:
            dfs.append(df)

    all_df = pd.concat(dfs, ignore_index = True)
    all_df = assign_side(df = all_df, p_df = p_dti) # assign LesionSide
    all_df_flip = flip_lesion_dti(all_df) # flip lesion
    all_df_flip = add_metrics(all_df_flip) # add metrics (MD, RD), rename eigenvalues (e.g. EgVal0 = lambda_1)

    # exclude subjs without LesionSide
    no_assigned_lesion = all_df_flip[all_df_flip.LesionSide.isna()]['subj_id'].unique()
    all_df_flip = all_df_flip[~all_df_flip.subj_id.isin(no_assigned_lesion)]

  
    all_df_flip.to_csv(os.path.join(gl.baseDir, 'DTI', 'JHU_MNI_DTI_flip.tsv'), sep='\t', index=False)
    