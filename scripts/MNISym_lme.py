#%%
import pandas as pd
import os
from pathlib import Path
import nibabel as nib

from smarts_cerebellum import lme
from smarts_cerebellum import mirror_lesion
import smarts_cerebellum.globals as gl
from smarts_cerebellum.util import subj_week_loop


p_df = pd.read_csv(f'{gl.baseDir}/participants_anat.tsv', sep = '\t')
patients_df = p_df[p_df.isPatient == 1]
controls_df = p_df[p_df.isPatient == 0]
left_lesion_df = patients_df[patients_df.LesionSide == 'left '] # patients with left lesion - need to flip their images


week_idx_dict = {
    'W0': 0,
    'W4': 1,
    'W12': 2,
    'W24': 3,
    'W52': 4
}

# only need to do the actual flip once; then we can comment those lines out? Or make the funciton have the option to run the flip or just search for the file path (or new fcn for switch path_name?)
def flip_left_lesion(subj_path_dict, df, path, space, segment): # df = patients with left lesion
    for subj, week in subj_week_loop(df):
        flip = f'{path}/{subj}/{subj}_{week}_{space}_{segment}_coreg_reslice.nii.gz'

        if not Path(flip).is_file():
            continue
        
        flipped = mirror_lesion.FlipLR(flip)

        save_path =  f'{path}/{subj}/{subj}_{week}_{space}_{segment}_coreg_reslice_FlipLR.nii.gz'
        
        # save flipped image
        nib.save(flipped, save_path)

        # for patient with flipped image: replace their file path in dict with path to flipped image
        subj_path_dict[week_idx_dict[week]][subj] = save_path

    return subj_path_dict


def patients_run_lme(segment):

    # patients need to flip their lesion (if LH lesion)
    ref_subj = 'CU_2310'
    subdir = f'MNISym_{segment}'
    file_suffix = f'MNISym_{segment}_coreg_reslice.nii.gz'
    subpath = os.path.join(gl.baseDir, subdir)
    space = 'MNISym'
    

    # for saving lme output files
    results_path = os.path.join(gl.baseDir, 'lme', f'{segment}')
    prefix = f'patients_MNISymC_{segment}'

    
    # for each week: make dict with subjects and their file paths
    subj_path_dict_patient = lme.make_week_dicts(df = patients_df, ref_subj = ref_subj, subdir = subdir, file_suffix = file_suffix)

    # use flipped image for left lesion patients (so that lesion on right)
    subj_path_dict_patient = flip_left_lesion(subj_path_dict = subj_path_dict_patient, df = left_lesion_df, path = subpath, space = space, segment = segment)


    B, S, status_list = lme.main(subj_path_dict = subj_path_dict_patient, df = patients_df,
                                                                            results_path = results_path, prefix = prefix)


    # save convergence status to dataframe
    patients_status_df = pd.DataFrame(status_list)
    patients_status_df['patient_voxel']=1
    patients_status_df['model'] = 'lme_intercept'
    patients_status_df.to_csv(f'{results_path}/patients_voxel_status_{segment}.tsv', sep = '\t', index = False)

    print(f'patients {segment} done!')



def controls_run_lme(segment):
    ref_control = 'UZP_1001'
    subdir = f'MNISym_{segment}'
    file_suffix = f'MNISym_{segment}_coreg_reslice.nii.gz'



    # for saving lme output files
    results_path = os.path.join(gl.baseDir, 'lme', f'{segment}')
    prefix = f'patients_MNISymC_{segment}'


    subj_path_dict_controls = lme.make_week_dicts(df = controls_df, ref_subj = ref_control, subdir = subdir, file_suffix = file_suffix)

    B_c, S_c, status_list_c = lme.main(subj_path_dict = subj_path_dict_controls, df = controls_df,
                                                                                        results_path = results_path, prefix = prefix)

    # save convergence status to dataframe
    controls_status_df = pd.DataFrame(status_list_c)
    controls_status_df['patient_voxel']=0
    controls_status_df['model'] = 'lme_intercept'
    controls_status_df.to_csv(f'{results_path}/controls_voxel_status_{segment}.tsv', sep = '\t', index = False)

    print(f'controls {segment} done!')




#%%
# PATIENTS
#patients_run_lme('T1')
patients_run_lme('GM')
patients_run_lme('WM')
patients_run_lme('CSF')

# CONTROLS
#controls_run_lme('T1')
controls_run_lme('GM')
controls_run_lme('WM')
controls_run_lme('CSF')
