import pandas as pd
import nibabel as nib
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum import summary_img as si

# MACROS
template_path = os.path.join(gl.baseDir, 'ROI', 'tpl-MNI152NLin2009cSymC_T1w.nii')
template_img = nib.load(template_path)

# EXCLUDING SOME SUBJS
p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
p_df = p_df[~p_df.subj_id.isin(gl.bad)]

left_lesion_df = p_df[p_df.LesionSide == 'left ']

patients_df = p_df[p_df.isPatient == 1]
controls_df = p_df[p_df.isPatient == 0]

space = 'MNISymC'
segments = ['WM', 'GM', 'CSF']
weeks = ['W0', 'W4', 'W12', 'W24', 'W52']

for segment in segments:
    seg_dir = f'{space}_{segment}'
    for week in weeks:
        si.mean_image_right(group = 'patients',
                            group_df = patients_df,
                            left_lesion_df = left_lesion_df,
                            template_img = template_img,
                            search_dir = seg_dir,
                            segment = segment,
                            metric = '_mod',
                            week = week)
        
        si.mean_image_right(group = 'controls',
                            group_df = controls_df,
                            left_lesion_df = left_lesion_df,
                            template_img = template_img,
                            search_dir = seg_dir,
                            segment = segment,
                            metric = '_mod',
                            week = week)

t1_dir = f'{space}_T1'
for week in weeks:
    si.mean_image_right(group = 'patients',
                            group_df = patients_df,
                            left_lesion_df = left_lesion_df,
                            template_img = template_img,
                            search_dir = t1_dir,
                            segment = 'T1',
                            metric = '',
                            week = week)
    si.mean_image_right(group = 'controls',
                            group_df = controls_df,
                            left_lesion_df = left_lesion_df,
                            template_img = template_img,
                            search_dir = t1_dir,
                            segment = 'T1',
                            metric = '',
                            week = week)

