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
    roi_tract = 'MCP'
    label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.nii')


    if roi_tract == 'MCP':
        region_names = [''] * 2 + [f'{roi_tract}_L', f'{roi_tract}_R']
    elif roi_tract == 'CST':
        region_names = [''] * 13 + [f'{roi_tract}_L', f'{roi_tract}_R']
    else:
        raise ValueError(f'invalid tract {roi_tract}')

        
    tract_segments = ['WM_mod']
    tract_folders = [f'{space}_WM']
    for t_segment, t_folder in zip(tract_segments, tract_folders):
        lme_main(group = 'patients', p_df = patients_df, segment = t_segment, folder = t_folder, 
            label_image = label_image, region_names = region_names, roi = roi_tract, space = space)
        lme_main(group = 'controls', p_df = controls_df, segment = t_segment, folder = t_folder,
                    label_image = label_image, region_names = region_names, roi = roi_tract, space = space)



    # custom ROIs (at different levels)
    # roi_tract = 'CST'
    # levels = ['midbrain', 'pons', 'medulla']

    # tract_segments = ['WM_mod']
    # tract_folders = [f'{space}_WM']

    # for level in levels:
    #     label_image = os.path.join(gl.baseDir, 'ROI', f'{space}.{roi_tract}.{level}.nii')
    #     region_names = [''] * 13 + [f'left_{roi_tract}', f'right_{roi_tract}']

    #     for t_segment, t_folder in zip(tract_segments, tract_folders):
    #         lme_main(group = 'patients', p_df = patients_df, segment = t_segment, folder = t_folder, label_image = label_image, region_names = region_names, roi = f'{roi_tract}_{level}')
    #         lme_main(group = 'controls', p_df = controls_df, segment = t_segment, folder = t_folder, label_image = label_image, region_names = region_names, roi = f'{roi_tract}_{level}')

