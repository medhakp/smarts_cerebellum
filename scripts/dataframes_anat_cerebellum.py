import pandas as pd
import SUITPy as suit
import smarts_cerebellum.globals as gl
import os
from smarts_cerebellum.dataframes import make_dataframe_atlas_space
import numpy as np

MODES = {
    'normalized': dict(param = '', use_weeks = True, folder = '{space}_GM', w0_only = False),
    'slope': dict(param = '_slope', use_weeks = False, folder = 'regression', w0_only = True)
}

atlases = {
    'left_right': dict(roi = 'atl-NettekovenSym_LeftRight_MNISymC.nii', 
                        roi_labels = [''] * 0 + ['cerebellum_L', 'cerebellum_R'],
                        save_name = 'Nettekoven_LeftRight'),

    'mads': dict(roi='atl-NettekovenSym_MADS_MNISymC.nii', 
                    roi_labels = [''] * 0 + ['M_L', 'A_L', 'D_L', 'S_L', 'M_R', 'A_R', 'D_R', 'S_R'],
                    save_name = 'Nettekoven_MADS'),
    
    '32_region': dict(atlas = 'Nettekoven_2024',
                        maps = 'atl-NettekovenSym32',
                        save_name = None)
    }

def summary_df(
               p_df,
               space,
               segment,
               mode,

               # built-in atlas (from DiedrichsenLab)
               atlas = None,
               maps = None,

               # custom atlas
               roi = None,
               roi_labels = None,

               save_name = None,
               ):
    
    config = MODES[mode]
    folder = config['folder'].format(space = space) # MNISymC
    if config['w0_only']:
        p_df = p_df.sort_values("Week").groupby("subj_id", as_index=False).first()

    df = make_dataframe_atlas_space(
        p_df = p_df,
        folder = folder,
        segment = segment,
        param = config['param'],
        the_atlas = atlas,
        maps = maps,
        use_weeks = config['use_weeks'],
        label_image = roi,
        region_names = roi_labels
    )

    df['hemisphere']=  df.regionname.str[-1]
    df['side'] = np.where(df.isPatient == 0, 'controls', np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
    

    if not atlas == None:
        save_name = atlas
    else:
        save_name = save_name
    
    df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{save_name}_{segment}{config["param"]}.tsv'), sep='\t', index=False)

if __name__=='__main__':
    # these can be changed
    mode = 'normalized' # 'slope', 'normalized'
    run_atlases = ['mads']

    space = 'MNISymC'
    segment = 'GM_mod'
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    roi_dir = os.path.join(gl.baseDir, 'ROI', 'Nettekoven_atlases')


    for run_atlas in run_atlases:
        kwargs = dict(atlases[run_atlas])

        # find roi in directory
        if 'roi' in kwargs:
            kwargs['roi'] = os.path.join(roi_dir, kwargs['roi'])
            
        summary_df(p_df = p_df, space = space, segment = segment, mode = mode, **kwargs)
  
