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
    folders = [f'{space}_WM']

    #param = '_slope'
    param = '' # for just normalized images

    # if summarizing normalized images: param = '', [fcn_call] use_weeks = True, folder = folder, p_df = p_df (when use_weeks = True)
    # if summarizing slope images: param = '_slope', [fcn call] use_weeks = False (or leave out), folder = 'regression', p_df = p_df_w0 (when use_weeks = False)
    
    levels = ['midbrain', 'pons', 'medulla']

    for level in levels:
        # atlas
        label_image=os.path.join(gl.baseDir, 'ROI', f'MNISymC.CST.{level}.nii')
        region_names = [''] * 13 + [f'{level}_CSTL', f'{level}_CSTR']
        for segment, folder in zip(segments, folders):
            #folder = 'regression'
            df = make_dataframe_atlas_space(
                #p_df=p_df_w0,
                p_df = p_df,
                #folder = 'regression',
                folder = folder,
                region_names= region_names,
                segment = segment,
                param = param,
                label_image = label_image,
                use_weeks = True,
            )
            df['hemisphere'], df['regionname'] = df.regionname.str[-1], df.regionname.str[:-1]
            df['group'] = np.where(df.isPatient == 0, 'controls', np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
            #df = df.groupby(['subj_id', 'regionname', 'group']).mean(numeric_only=True).reset_index() # used for slopes
            df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_CST_{level}_{segment}{param}.tsv'), sep='\t', index=False)