import pandas as pd
import SUITPy as suit
import smarts_cerebellum.globals as gl
import os
from smarts_cerebellum.dataframes import make_dataframe_atlas_space
import numpy as np


if __name__=='__main__':
    #REGRESSION SLOPE DATAFRAMES
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    p_df_w0 = p_df.sort_values("Week").groupby("subj_id", as_index=False).first()
    
    space = 'MNISymC'
    segments = ['T1','GM_mod', 'CSF_mod']
    folders = [f'{space}_T1', f'{space}_GM', f'{space}_CSF']

    param = '_slope'

    # atlas
    the_atlas = 'Nettekoven_2024'
    maps = 'atl-NettekovenSym32'

    for segment, folder in zip(segments, folders):
        df = make_dataframe_atlas_space(
            p_df=p_df_w0,
            folder = 'regression',
            segment = segment,
            param = param,
            the_atlas = the_atlas,
            maps = maps,
        )
        df['hemisphere'], df['regionname'] = df.regionname.str[-1], df.regionname.str[:-1]
        df['group'] = np.where(df.isPatient == 0, 'controls', np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
        df.to_csv(os.path.join(gl.baseDir, 'regression', f'summary_{space}_{the_atlas}_{segment}{param}.tsv'), sep='\t', index=False)
