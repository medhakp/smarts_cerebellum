import pandas as pd
import SUITPy as suit
import smarts_cerebellum.globals as gl
import os
from smarts_cerebellum.dataframes import make_dataframe_atlas_space
import numpy as np


if __name__=='__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    p_df_w0 = p_df.sort_values("Week").groupby("subj_id", as_index=False).first()
    
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