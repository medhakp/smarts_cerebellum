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



#%%

# patients
ref_subj = 'CU_2310'
subdir = 'MNISym_T1'
file_suffix = 'MNISym_T1_coreg_reslice.nii.gz'
subpath = os.path.join(gl.baseDir, subdir)
space = 'MNISym'
segment = 'T1'

# for saving lme output files
results_path = os.path.join(gl.baseDir, 'lme')
prefix = 'patients_MNISymC_T1'



#%%
# for each week: make dict with subjects and their file paths
subj_path_dict_patient = lme.make_week_dicts(df = patients_df, ref_subj = ref_subj, subdir = subdir, file_suffix = file_suffix)

# use flipped image for left lesion patients (so that lesion on right)
subj_path_dict_patient = flip_left_lesion(subj_path_dict = subj_path_dict_patient, df = left_lesion_df, path = subpath, space = space, segment = segment)

#%%
betas, B, beta_images, binary_mask, mask_images, status_list = lme.main(subj_path_dict = subj_path_dict_patient, df = patients_df,
                                                                        results_path = results_path, prefix = prefix)


# save convergence status to dataframe
patients_status_df = pd.DataFrame(status_list)
patients_status_df['patient_voxel']=1
patients_status_df['model'] = 'lme_intercept'
patients_status_df.to_csv(f'{results_path}/patients_voxel_status.tsv', sep = '\t', index = False)




#%%
# controls
ref_control = 'UZP_1001'


prefix_controls = 'controls_MNISymC_T1'


subj_path_dict_controls = lme.make_week_dicts(df = controls_df, ref_subj = ref_control, subdir = subdir, file_suffix = file_suffix)

betas_c, B_c, beta_images_c, binary_mask_c, mask_images_c, status_list_c = lme.main(subj_path_dict = subj_path_dict_controls, df = controls_df,
                                                                                    results_path = results_path, prefix = prefix_controls)

# save convergence status to dataframe
controls_status_df = pd.DataFrame(status_list_c)
controls_status_df['patient_voxel']=0
controls_status_df['model'] = 'lme_intercept'
controls_status_df.to_csv(f'{results_path}/controls_voxel_status.tsv', sep = '\t', index = False)
