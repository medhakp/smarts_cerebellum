import pandas as pd
import os

from smarts_cerebellum import lme
import smarts_cerebellum.globals as gl

# paths for file searching
#____________________________________________
# normalized T1 files (in MNISymC space)
ref_subj = 'CU_2310'
subdir = 'MNISym_T1'
file_suffix = 'MNISym_T1_coreg_reslice.nii.gz'

save_folder = 'lme'

#_____________________________________________

p_df = pd.read_csv(f'{gl.baseDir}/participants_anat.tsv', sep = '\t')


# subject-week path dicts: for each week, dict is: subj_id: subj_path; for each of w weeks, its dict is in list position w-1
subj_path_dict = lme.make_week_dicts(df = p_df, ref_subj = ref_subj, subdir = subdir, file_suffix = file_suffix)

betas, B, beta_images = lme.main(subj_path_dict = subj_path_dict, df = p_df)

# save images
save_path = os.path.join(gl.baseDir, save_folder)