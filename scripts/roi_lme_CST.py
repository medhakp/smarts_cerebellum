import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_anat

# anatomicals
p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
patients_df = p_df[p_df.isPatient == 1]
controls_df = p_df[p_df.isPatient == 0]

space = 'MNISymC'

# custom ROI
roi_tract = 'CST'
label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.nii')
region_names = [''] * 13 + [f'left_{roi_tract}', f'right_{roi_tract}']
    
tract_segments = ['T1', 'WM_mod']
tract_folders = [f'{space}_T1', f'{space}_WM']
for t_segment, t_folder in zip(tract_segments, tract_folders):
    lme_anat(group = 'patients', p_df = patients_df, segment = t_segment, folder = t_folder, 
        label_image = label_image, region_names = region_names, rois = roi_tract)
    lme_anat(group = 'controls', p_df = controls_df, segment = t_segment, folder = t_folder,
                label_image = label_image, region_names = region_names, rois = roi_tract)



# custom ROIs (at different levels)
# roi_tract = 'CST'
# levels = ['midbrain', 'pons', 'medulla']

# tract_segments = ['WM_mod']
# tract_folders = [f'{space}_WM']

# for level in levels:
#     label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.{level}.nii')
#     region_names = [''] * 13 + [f'left_{roi_tract}', f'right_{roi_tract}']

#     for t_segment, t_folder in zip(tract_segments, tract_folders):
#         lme_anat(group = 'patients', p_df = patients_df, segment = t_segment, folder = t_folder, label_image = label_image, region_names = region_names, rois = f'{roi_tract}_{level}')
#         lme_anat(group = 'controls', p_df = controls_df, segment = t_segment, folder = t_folder, label_image = label_image, region_names = region_names, rois = f'{roi_tract}_{level}')

