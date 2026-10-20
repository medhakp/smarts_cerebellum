import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_main

if __name__ == '__main__':

    roi_tract = 'MCP'

    # anatomicals
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    patients_df = p_df[p_df.isPatient == 1]
    controls_df = p_df[p_df.isPatient == 0]

    space = 'MNISymC'
    label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.nii')


    if roi_tract == 'MCP':
        region_names = [''] * 2 + [f'{roi_tract}_L', f'{roi_tract}_R']
    elif roi_tract == 'CST':
        region_names = [''] * 13 + [f'{roi_tract}_L', f'{roi_tract}_R']
    else:
        raise ValueError(f'invalid tract {roi_tract}')
    

    # predictors df (x_df) - use obs values.
    x_df = pd.read_csv(os.path.join(gl.baseDir, f'{space}_WM', f'summary_{space}_{roi_tract}_WM_mod.tsv'), sep = '\t')
    x_df_patients = x_df[x_df.isPatient == 1]
    x_df_controls = x_df[x_df.isPatient == 0]
    

        
    tract_segments = ['WM_mod']
    tract_folders = [f'{space}_WM']
    for t_segment, t_folder in zip(tract_segments, tract_folders):
        lme_main(group = 'patients', p_df = patients_df, segment = t_segment, folder = t_folder, 
            label_image = label_image, region_names = region_names, roi = roi_tract, space = space,
            predictors_df = x_df_patients, stat = 'mean')
        lme_main(group = 'controls', p_df = controls_df, segment = t_segment, folder = t_folder,
                    label_image = label_image, region_names = region_names, roi = roi_tract, space = space,
                    predictors_df = x_df_controls, stat = 'mean')


