import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum.roi_lme import lme_main

atlases = {
    'left_right': dict(roi = 'atl-NettekovenSym_LeftRight_MNISymC.nii', 
                        roi_labels = [''] * 0 + ['cerebellum_L', 'cerebellum_R'],
                        save_name = 'Nettekoven_LeftRight'),

    'mads': dict(roi='atl-NettekovenSym_MADS_MNISymC.nii', 
                    roi_labels = [''] * 0 + ['M_L', 'A_L', 'D_L', 'S_L', 'M_R', 'A_R', 'D_R', 'S_R'],
                    save_name = 'Nettekoven_MADS'),
    
    '32_region': dict(atlas = 'Nettekoven_2024',
                        maps = 'atl-NettekovenSym32',
                        save_name = None)
    }

def run_lme(
            p_df,
            space,
            atlas_space,
            segment,
            folder = None,

            # built-in atlas (from DiedrichsenLab)
            atlas = None,
            maps = None,

            # custom atlas
            roi = None,
            roi_labels= None,

            save_name = None
            ):
    if not atlas == None:
        save_name = atlas
    
    x_df = pd.read_csv(os.path.join(gl.baseDir, folder, f'summary_MNISymC_{save_name}_{segment}.tsv'), sep = '\t')
    patients_df = p_df[p_df.isPatient == 1]
    controls_df = p_df[p_df.isPatient == 0]

    lme_main(group = 'patients',
             p_df = patients_df,
             segment = segment,
             folder = folder,
             atlas_space = atlas_space,
             space = space,
             atlas = save_name,
             maps = maps,
             label_image = roi,
             region_names = roi_labels,
             predictors_df = x_df[x_df.isPatient == 1],
             save_name = save_name
             )

    lme_main(group = 'controls',
            p_df = controls_df,
            segment = segment,
            folder = folder,
            atlas_space = atlas_space,
            space = space,
            atlas = save_name,
            maps = maps,
            label_image = roi,
            region_names = roi_labels,
            predictors_df = x_df[x_df.isPatient == 0],
            save_name = save_name
            )


if __name__ == '__main__':

    run_atlases = ['mads']

    # anatomicals
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    
    space = 'MNISymC'
    atlas_space = 'MNISym'

    cereb_segment ='GM_mod'
    cereb_folder = f'{space}_GM'
    roi_dir = os.path.join(gl.baseDir, 'ROI', 'Nettekoven_atlases')

    for run_atlas in run_atlases:
        kwargs = dict(atlases[run_atlas])
        if 'roi' in kwargs:
            kwargs['roi'] = os.path.join(roi_dir, kwargs['roi'])

        run_lme(p_df = p_df,
                space = space,
                atlas_space = atlas_space,
                segment = cereb_segment,
                folder = cereb_folder,
                **kwargs)

