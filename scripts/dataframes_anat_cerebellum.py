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

def summary_df(
               p_df,
               space,
               segment,
               mode,
               atlas = None,
               maps = None,
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
        df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{atlas}_{segment}{config["param"]}.tsv'), sep='\t', index=False)
    else:
        df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{save_name}_{segment}{config["param"]}.tsv'), sep='\t', index=False)

if __name__=='__main__':
    mode = 'normalized' # 'slope', 'normalized'
    space = 'MNISymC'

    # atlas = 'Nettekoven_2024'
    # maps = 'atl-NettekovenSym32'

    segment = 'GM_mod'
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')

    # use custom ROI
    roi = os.path.join(gl.baseDir, 'ROI', 'Nettekoven_atlases', 'atl-NettekovenSym_LeftRight_MNISymC.nii')
    roi_labels = [''] * 0 + ['cerebellum_L', 'cerebellum_R']

    summary_df(p_df = p_df, space = space, segment = segment, roi = roi, roi_labels = roi_labels, mode = mode, save_name = 'NettekovenLeftRight')