import pandas as pd
import nibabel as nib
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum import summary_img as si

# MACROS
template_path = os.path.join(gl.baseDir, 'ROI', 'tpl-MNI152NLin2009cSymC_T1w.nii')
template_img = nib.load(template_path)

p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
left_lesion_df = p_df[p_df.LesionSide == 'left ']
patients_df = p_df[p_df.isPatient == 1]
controls_df = p_df[p_df.isPatient == 0]

segments = ['T1', 'WM_mod', 'GM_mod', 'CSF_mod']
for segment in segments:
    # patients: mean, median
    si.mean_image_right(group = 'patients', group_df = patients_df, left_lesion_df = left_lesion_df, template_img = template_img,
                        search_dir = 'regression', segment = segment, space = 'MNISymC', metric = '_slope')
    si.median_image_right(group = 'patients', group_df = patients_df, left_lesion_df = left_lesion_df, template_img = template_img,
                        search_dir = 'regression', segment = segment, space = 'MNISymC', metric = '_slope')
    
    # control: mean, median
    si.mean_image_right(group = 'controls', group_df = controls_df, left_lesion_df = left_lesion_df, template_img = template_img,
                        search_dir = 'regression', segment = segment, space = 'MNISymC', metric = '_slope')
    si.median_image_right(group = 'controls', group_df = controls_df, left_lesion_df = left_lesion_df, template_img = template_img,
                        search_dir = 'regression', segment = segment, space = 'MNISymC', metric = '_slope')