import pandas as pd
import os
import numpy as np
import smarts_cerebellum.globals as gl
from smarts_cerebellum.dataframes import make_dataframe_atlas_space

MODES = {
    'normalized': dict(param = '', use_weeks = True, folder = 'MNISymC_WM', w0_only = False, average = False),
    'slope': dict(param = '_slope', use_weeks = False, folder = 'regression', w0_only = True, average = True),
    'jacobian': dict(param = '', use_weeks = True, folder = 'MNISymC_trans', w0_only = False, average = False, week_dir = True)
    
    }

def summary_df(
               p_df,
               space,
               segment,
               atlas,
               region_names,
               mode,
               folder = None,
               label_image = None
               ):
    config = MODES[mode]
    if not folder == None:
        folder = folder
    else:
        folder = config['folder'].format(space = space) # MNISymC

    if config['w0_only']:
        p_df = p_df.sort_values("Week").groupby("subj_id", as_index=False).first()
    if label_image == None:
        label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{atlas}.nii')

    df = make_dataframe_atlas_space(
        p_df = p_df,
        folder = folder,
        region_names = region_names,
        segment = segment,
        param = config['param'],
        label_image = label_image,
        use_weeks = config['use_weeks']  ,
        week_dir = config.get('week_dir', False)
    )

    df['hemisphere'], df['region_bilat'] = df.regionname.str[-1], df.regionname.str[:-1]
    df['side'] = np.where(df.isPatient == 0, 'controls', 
                          np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
    
    if config['average']:
        df = df.groupby(['subj_id', 'regionname', 'side']).mean(numeric_only=True).reset_index() # used for slopes
        
    df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{atlas}_{segment}{config["param"]}.tsv'), sep='\t', index=False)

    
if __name__=='__main__':

    mode = 'normalized' # 'slope', 'normalized', 'jacobian'
    atlas = 'CST' # 'CST', 'MCP', 'pons'
    
    space = 'MNISymC'
    #segment = 'WM_mod' # mod volume (assume reflects volume)
    #segment = 'T1_to-MNI152NLin2009cSymC_mode-image_detJ' # FOR JACOBIAN
    segment = 'WM'
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')

    if atlas == 'CST':
        region_names = [''] * 13 + ['CST_L', 'CST_R']
    elif atlas == 'MCP':
        region_names = [''] * 2 + ['MCP_L', 'MCP_R']
    elif atlas == 'pons':
        region_names = [''] * 1 + ['pons_L', 'pons_R']
    elif atlas == 'CST_medulla':
        region_names = [''] * 13 + ['CSTmedulla_L', 'CSTmedulla_R']
    elif atlas == 'CST_pons':
        region_names = [''] * 13 + ['CST_pons_L', 'CST_pons_R']
    else:
        raise ValueError(f'invalid atlas: {atlas}')

    summary_df(p_df = p_df, space = space, atlas = atlas, 
               region_names = region_names, segment = segment, mode = mode,
               label_image = os.path.join(gl.baseDir, 'ROI', f'MNISymC.{atlas}.nii'), 
               folder = 'MNISymC_WM'
               )
    