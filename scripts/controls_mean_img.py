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

from smarts_cerebellum import make_summed_image
import smarts_cerebellum.globals as gl

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


# first: make week dicts for each segment

def controls_average(segment, space = 'MNISym', 
                     df = controls_df, ref_subj = ref_subj,
                     weeks_int = weeks_int, time_points = time_points,
                     save_dir = os.path.join(gl.baseDir, 'temporary'),
                     metric = 'mean', template = template_img,
                     pfx = pfx, sfx = sfx):
    
    subdir = os.path.join(gl.baseDir, f'{space}_{segment}')
    file_suffix = f'{space}_{segment}_coreg_reslice.nii.gz'

    subj_week_paths = make_summed_image.make_week_dicts(df = df, ref_subj = ref_subj, 
                                                        subdir = subdir, file_suffix = file_suffix,
                                                         time_points = weeks_int)
    
    # save images
    prefix = f'{pfx}_{segment}'

    make_summed_image.main(prefix = prefix, suffix = sfx, save_dir = save_dir,
                           subj_path_dict=subj_week_paths, weeks = time_points,
                           template = template, metric = metric)
    
controls_average('T1')

# in temporary: (e.g.) W4 image average looks the exact same as the lme average image.

# %%
space = 'MNISym', 
df = controls_df
ref_subj = 'UZP_1001'
weeks_int = [0, 4, 12, 24, 52]
time_points = ['W0', 'W4', 'W12', 'W24', 'W52']
space = 'MNISym'
segment = 'T1'
subdir = os.path.join(gl.baseDir, f'{space}_{segment}')
file_suffix = f'{space}_{segment}_coreg_reslice.nii.gz'


subj_week_paths = make_summed_image.make_week_dicts(df = df, ref_subj = ref_subj, 
                                                        subdir = subdir, file_suffix = file_suffix,
                                                         time_points = weeks_int)

