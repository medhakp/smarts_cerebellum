import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_main

# FaMap
p_df = pd.read_excel(os.path.join(gl.baseDir, 'DTI', 'patient_list.xlsx'), usecols = range(10))
p_df['subj_id'] = p_df['Centre'].str.strip() + '_' + p_df['ID'].astype(str)

space = 'MNISymC'

# custom ROI
roi_tract = 'CST'
label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.nii')
region_names = [''] * 13 + [f'left_{roi_tract}', f'right_{roi_tract}']

segment = 'FaMap'
folder = f'{space}_{segment}'
lme_main(group = 'patients', p_df = p_df, segment = segment, folder = folder, space = 'MNISymC',
         label_image = label_image, region_names = region_names, rois = roi_tract)
