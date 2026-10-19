import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_main

if __name__ == '__main__':

    # anatomicals
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    patients_df = p_df[p_df.isPatient == 1]
    controls_df = p_df[p_df.isPatient == 0]

    space = 'MNISymC'

    # cerebellar atlas
    atlas_space = 'MNISym'
    atlas = 'Nettekoven_2024'
    maps = 'atl-NettekovenSym32'



    cereb_segments = ['FaMap']
    cereb_folders = [f'{space}_FaMap']

    # predictors df (x_df) - use obs values.
    x_df = pd.read_csv(os.path.join(gl.baseDir, 'MNISymC_FaMap', f'summary_MNISymC_{atlas}_FaMap.tsv'), sep = '\t')
    x_df = x_df[~x_df.regionname.str.endswith('_R')].copy()
    x_df['regionname'] = x_df['regionname'].str.replace(r'_L$', f'_ai', regex=True)


    for c_segment, c_folder in zip(cereb_segments, cereb_folders):
        lme_main(group = 'patients', p_df = patients_df, segment = c_segment, folder = c_folder, 
                    atlas_space = atlas_space, atlas = atlas, maps = maps, roi = atlas,
                    predictors_df= x_df, stat = 'asymmetry_index')
