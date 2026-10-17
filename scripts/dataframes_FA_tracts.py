import pandas as pd
import os
import numpy as np
import smarts_cerebellum.globals as gl
from smarts_cerebellum.dataframes import make_dataframe_atlas_space
from smarts_cerebellum.dti_normalized_metrics import add_normalized_metrics


if __name__=='__main__':


    # demographics not available in "patient_list"; for now, we can just use the T1 patient list
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    p_df = p_df[p_df.isPatient == 1]
    
    space = 'MNISymC'
    segments = ['FaMap']
    folders = [f'{space}_FaMap']
    param = ''

    atlas = '' # 'CST', 'MCP'
    if atlas == 'CST':
        region_names = [''] * 13 + ['CST_L', 'CST_R']
    elif atlas == 'MCP':
        region_names = [''] * 2 + ['MCP_L', 'MCP_R']
    else:
        raise ValueError(f'invalid atlas: {atlas}')
    
    label_image=os.path.join(gl.baseDir, 'ROI', f'MNISymC.{atlas}.nii')

    
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
        df['side'] = np.where(df.isPatient == 0, 'controls', np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
        
        # here, we should also calculate our metrics: ratio, log_ratio, asymmetry index
        df = add_normalized_metrics(df)

        df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{atlas}_{segment}{param}.tsv'), sep='\t', index=False)