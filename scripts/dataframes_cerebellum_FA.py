import pandas as pd
import SUITPy as suit
import smarts_cerebellum.globals as gl
import os
from smarts_cerebellum.dataframes import make_dataframe_atlas_space
from smarts_cerebellum.dti_normalized_metrics import add_normalized_metrics
import numpy as np


if __name__=='__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep='\t')
    
    space = 'MNISymC'
    segments = ['FaMap']
    folders = [f'{space}_FaMap']

    # atlas
    the_atlas = 'Nettekoven_2024'
    maps = 'atl-NettekovenSym32'

    for segment, folder in zip(segments, folders):
        df = make_dataframe_atlas_space(
            p_df=p_df,
            folder = 'MNISymC_FaMap',
            use_weeks = True,
            param = '',
            segment = segment,
            the_atlas = the_atlas,
            maps = maps,
        )
        df['hemisphere'], df['region_bilat'] = df.regionname.str[-1], df.regionname.str[:-1]
        df['side'] = np.where(df.isPatient == 0, 'controls', np.where(df.hemisphere == 'L', 'contralesional', 'ipsilesional'))
        df = add_normalized_metrics(df)
        df.to_csv(os.path.join(gl.baseDir, 'MNISymC_FaMap', f'summary_{space}_{the_atlas}_{segment}.tsv'), sep='\t', index=False)
