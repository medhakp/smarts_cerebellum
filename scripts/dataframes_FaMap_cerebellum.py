import pandas as pd
import smarts_cerebellum.globals as gl
import os
from smarts_cerebellum.dataframes import make_dataframe_atlas_space
from smarts_cerebellum.dti_normalized_metrics import add_normalized_metrics
import numpy as np


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

def summary_df(p_df,
               space,
               segment,
               folder = None,

               # built-in atlas (from DiedrichsenLab)
               atlas = None,
               maps = None,

               # custom atlas
               roi = None,
               roi_labels = None,

               save_name = None
               ):
    if not atlas == None:
        save_name = atlas
   
    df = make_dataframe_atlas_space(
            p_df=p_df,
            folder = folder,
            use_weeks = True,
            param = '',
            segment = segment,
            the_atlas = atlas,
            maps = maps,
            label_image = roi,
            region_names = roi_labels
    )

    df['hemisphere'], df['region_bilat'] = df.regionname.str[-1], df.regionname.str[:-1]
    df['side'] = np.where(df.isPatient == 0, 'controls', np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
    df = add_normalized_metrics(df)
    df.to_csv(os.path.join(gl.baseDir, folder, f'summary_{space}_{save_name}_{segment}.tsv'), sep='\t', index=False)



if __name__=='__main__':
    run_atlases = ['left_right', 'mads']

    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    p_df = p_df[p_df.isPatient == 1]
    
    space = 'MNISymC'
    segment = 'FaMap'
    folder = f'{space}_FaMap'

    roi_dir = os.path.join(gl.baseDir, 'ROI', 'Nettekoven_atlases')


    for run_atlas in run_atlases:
        kwargs = dict(atlases[run_atlas])

        # find roi in directory
        if 'roi' in kwargs:
            kwargs['roi'] = os.path.join(roi_dir, kwargs['roi'])
            
        summary_df(p_df = p_df, space = space, segment = segment, folder = folder, **kwargs)