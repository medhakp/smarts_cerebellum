#%%
# model image looks so strange for controls. For for controls, try getting image without model - just as-is

excluded_controls = ['CUP_1001']

# for this summed image, we need to use the normalized images; so need a more general function.
# path: smarts_cerebellum/MNISym_{segment}/{subj}/{subj}_{week}_MNISym_{segment}_coreg_reslice.nii.gz

# this funcmtion should just take a list of images instead of forming its own image path - so you just have to call the appropriate path-maker function

# so for each week: call subj_path_search function and return subj_paths, subj_available - store this in a dictionary

# get all the week dictionaries


#%%
import pandas as pd
import os
import nibabel as nib

import smarts_cerebellum.globals as gl
from smarts_cerebellum import overall_img
from smarts_cerebellum import make_summarized_dataframe_weeks as summ_df_weeks

p_df = pd.read_csv(f'{gl.baseDir}/participants_anat.tsv', sep = '\t')
controls_df = p_df[p_df.isPatient == 0]

# exclude CUP_1001
controls_df = controls_df[controls_df.subj_id != 'CUP_1001']


# MACROS
ref_subj = 'UZP_1001'
weeks_int = [0, 4, 12, 24, 52] # for make_dicts
time_points = ['W0', 'W4', 'W12', 'W24', 'W52']

pfx = 'controls_MNISymC'
sfx  = 'mean'

template_img = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'
template_img = nib.load(template_img)

space = 'MNISym'

# for dataframe
all_weeks = ['W0', 'W4', 'W12', 'W24', 'W52']
groups = ['controls']
metrics = ['mean']
segments = ['T1', 'GM', 'WM', 'CSF']
suffix0 = 'None'


# first: make week dicts for each segment

def controls_average(segment, space = space, df = controls_df,
                     ref_subj = ref_subj, weeks_int = weeks_int,

                     metric = 'mean', template = template_img,
                     pfx = pfx, sfx = sfx):
    
    subdir = os.path.join(gl.baseDir, f'{space}_{segment}')
    file_suffix = f'{space}_{segment}_coreg_reslice.nii.gz'

    subj_week_paths = overall_img.make_week_dicts(df = df, ref_subj = ref_subj, 
                                                        subdir = subdir, file_suffix = file_suffix,
                                                         weeks = weeks_int)

    # save images
    prefix = f'{pfx}_{segment}'
    save_dir = os.path.join(gl.baseDir, 'MNISymC_control_means', f'{segment}')

    overall_img.week_images(prefix = prefix, suffix = sfx, save_dir = save_dir,
                           subj_path_dict=subj_week_paths, weeks = time_points,
                           template = template, metric = metric)
    
controls_average('T1')
controls_average('GM')
controls_average('WM')
controls_average('CSF')

#%%
# then: put in dataframe
lme_dir = os.path.join(gl.baseDir, 'lme')
df_list = []
for gp in groups:
    for m in metrics:
        for s in segments:
            subdir = os.path.join(gl.baseDir,'MNISymC_control_means')
            df_list.append(summ_df_weeks.make_summ_df(group = gp, metric = m, segment = s,
                                                      suffix = 'mean', suffix0 = 'None',
                                                      weeks = all_weeks,
                                                      subdir = subdir
                                                      ))
summ_df = pd.concat(df_list, axis = 0, ignore_index = True)
#summ_df.to_csv(f'{lme_dir}/lme_summarized_df.tsv', sep = '\t', index = False)
summ_df['isModel'] = 0
summ_df.to_csv(f'{lme_dir}/controls_mean_summarized_df.tsv', sep = '\t', index = False)

# %%
