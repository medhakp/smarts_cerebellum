import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_anat

# anatomicals
p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
patients_df = p_df[p_df.isPatient == 1]
controls_df = p_df[p_df.isPatient == 0]

space = 'MNISymC'

# cerebellar atlas
atlas_space = 'MNISym'
atlas = 'Nettekoven_2024'
maps = 'atl-NettekovenSym32'



cereb_segments = ['T1', 'GM_mod']
cereb_folders = [f'{space}_T1', f'{space}_GM']

for c_segment, c_folder in zip(cereb_segments, cereb_folders):
    lme_anat(group = 'patients', p_df = patients_df, segment = c_segment, folder = c_folder, 
                atlas_space = atlas_space, atlas = atlas, maps = maps, rois = atlas)
    lme_anat(group = 'controls', p_df = controls_df, segment = c_segment, folder = c_folder,
                atlas_space = atlas_space, atlas = atlas, maps = maps, rois = atlas)
    