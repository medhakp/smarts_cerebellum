import pandas as pd
import os
import numpy as np
import smarts_cerebellum.globals as gl
from smarts_cerebellum.dataframes import make_dataframe_atlas_space

MODES = {
    'normalized': dict(param = '', use_weeks = True, folder = '{space}_WM', w0_only = False, average = False),
    'slope': dict(param = '_slope', use_weeks = False, folder = 'regression', w0_only = True, average = True)
}

def summary_df(
               p_df,
               space,
               segment,
               atlas,
               region_names,
               mode
               ):
    config = MODES[mode]
    folder = config['folder'].format(space = space) # MNISymC

    if config['w0_only']:
        p_df = p_df.sort_values("Week").groupby("subj_id", as_index=False).first()

    df = make_dataframe_atlas_space(
        p_df = p_df,
        folder = folder,
        region_names = region_names,
        segment = segment,
        param = config['param'],
        label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{atlas}.nii'),
        use_weeks = config['use_weeks']    
    )

    df['hemisphere'], df['region_bilat'] = df.regionname.str[-1], df.regionname.str[:-1]
    df['side'] = np.where(df.isPatient == 0, 'controls', 
                          np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
    
    if config['average']:
        df = df.groupby(['subj_id', 'regionname', 'side']).mean(numeric_only=True).reset_index() # used for slopes
        
    df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{atlas}_{segment}{config["param"]}.tsv'), sep='\t', index=False)

    
if __name__=='__main__':

    mode = 'normalized' # 'slope', 'normalized'
    atlas = 'MCP' # 'CST', 'MCP'
    
    space = 'MNISymC'
    segment = 'WM_mod'
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')

    if atlas == 'CST':
        region_names = [''] * 13 + ['CST_L', 'CST_R']
    elif atlas == 'MCP':
        region_names = [''] * 2 + ['MCP_L', 'MCP_R']
    else:
        raise ValueError(f'invalid atlas: {atlas}')

    summary_df(p_df = p_df, space = space, atlas = atlas, 
               region_names = region_names, segment = segment, mode = mode)
    