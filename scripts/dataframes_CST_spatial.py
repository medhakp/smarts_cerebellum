import pandas as pd
import smarts_cerebellum.globals as gl
import os
from smarts_cerebellum.dataframes import make_dataframe_atlas_space
import numpy as np


if __name__=='__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    p_df_w0 = p_df.sort_values("Week").groupby("subj_id", as_index=False).first()
    
    space = 'MNISymC'
    segments = ['WM_mod']
    folders = [f'{space}_T1', f'{space}_WM']

    param = '_slope'
    
    levels = ['midbrain', 'pons', 'medulla']

    for level in levels:
        # atlas
        label_image=os.path.join(gl.baseDir, 'ROI', f'MNISymC.CST.{level}.nii')
        region_names = [''] * 13 + [f'{level}_CSTL', f'{level}_CSTR']
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
            df.to_csv(os.path.join(gl.baseDir, 'regression', f'summary_{space}_CST_{level}_{segment}{param}.tsv'), sep='\t', index=False)