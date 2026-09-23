import pandas as pd
import SUITPy as suit
import smarts_cerebellum.globals as gl
import os
from smarts_cerebellum.dataframes import make_dataframe_atlas_space
import numpy as np


if __name__=='__main__':
    """
    # for anatomicals
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    p_df_w0 = p_df.sort_values("Week").groupby("subj_id", as_index=False).first() # use this if just one image per subject; otherwise, use p_df
    
    space = 'MNISymC'
    segments = ['T1', 'WM_mod']
    folders = [f'{space}_T1', f'{space}_WM']

    param = '_slope'

    # atlas
    label_image=os.path.join(gl.baseDir, 'ROI', 'MNISymC.CST.nii')
    region_names = [''] * 13 + ['CSTL', 'CSTR'] # regionnames count in SUITpy start for 1 but ours from 14

    for segment, folder in zip(segments, folders):
        df = make_dataframe_atlas_space(
            p_df=p_df_w0,
            folder = 'regression',
            region_names= region_names,
            segment = segment,
            param = param,
            label_image = label_image,
        )
        df['hemisphere'], df['regionname'] = df.regionname.str[-1], df.regionname.str[:-1]
        df['group'] = np.where(df.isPatient == 0, 'controls', np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
        df = df.groupby(['subj_id', 'regionname', 'group']).mean(numeric_only=True).reset_index()
        df.to_csv(os.path.join(gl.baseDir, 'regression', f'summary_{space}_CST_{segment}{param}.tsv'), sep='\t', index=False)
    
    """

    # for FaMap
    #p_df = pd.read_excel(os.path.join(gl.baseDir, 'DTI', 'patient_list.xlsx'), usecols = range(10))
    #p_df['subj_id'] = p_df['Centre'].str.strip() + '_' + p_df['ID'].astype(str)

    # demographics not available in "patient_list"; for now, we can just use the T1 patient list
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    
    space = 'MNISymC'
    segments = ['FaMap']
    folders = [f'{space}_FaMap']
    param = ''


    # atlas - CST
    tract = 'CST'
    label_image=os.path.join(gl.baseDir, 'ROI', 'MNISymC.CST.nii')
    region_names = [''] * 13 + ['CSTL', 'CSTR'] # regionnames count in SUITpy start for 1 but ours from 14

    # atlas - MCP
    # tract = 'MCP'
    # label_image=os.path.join(gl.baseDir, 'ROI', f'MNISymC.{tract}.nii')
    # region_names = [''] * 2 + [f'MCPL', f'MCPR'] # start at n-1 (e.g. in FSLEyes, we have 3, 4; so, start from 2 here)

    
    for segment, folder in zip(segments, folders):
        df = make_dataframe_atlas_space(
            p_df=p_df,
            folder = folder,
            region_names= region_names,
            segment = segment,
            param = param,
            label_image = label_image,
            use_weeks = True,
            stats = ['median', 'mean']
        )
        df['hemisphere'], df['region_bilat'] = df.regionname.str[-1], df.regionname.str[:-1]
        df['group'] = np.where(df.isPatient == 0, 'controls', np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
        df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{tract}_{segment}{param}.tsv'), sep='\t', index=False)