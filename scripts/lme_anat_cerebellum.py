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
    # atlas_space = 'MNISym'
    # atlas = 'Nettekoven_2024'
    # maps = 'atl-NettekovenSym32'

    # custom ROI
    roi = os.path.join(gl.baseDir, 'ROI', 'Nettekoven_atlases', 'atl-NettekovenSym_LeftRight_MNISymC.nii')
    roi_labels = [''] * 0 + ['cerebellum_L', 'cerebellum_R']
    atlas = 'NettekovenLeftRight'
    atlas_space = 'MNISym'

    x_df = pd.read_csv(os.path.join(gl.baseDir, 'MNISymC_GM', f'summary_MNISymC_{atlas}_GM_mod.tsv'), sep = '\t')
 


    cereb_segments = ['GM_mod']
    cereb_folders = [f'{space}_GM']

    for c_segment, c_folder in zip(cereb_segments, cereb_folders):
        lme_main(group = 'patients', p_df = patients_df, segment = c_segment, folder = c_folder, 
                    atlas_space = atlas_space, space = space, atlas = atlas, roi = atlas,predictors_df = x_df[x_df.isPatient == 1])
        lme_main(group = 'controls', p_df = controls_df, segment = c_segment, folder = c_folder,
                    atlas_space = atlas_space, space = space, atlas = atlas, roi = atlas, predictors_df = x_df[x_df.isPatient == 0])
        