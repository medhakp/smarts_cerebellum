#%%
import numpy as np
import nibabel as nib
import os

import smarts_cerebellum.globals as gl

lme_dir = os.path.join(gl.baseDir, 'lme')


# get the sum of images - e.g. from lme, get the total voxel intensity for that week

# template
template_img = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'
template_img = nib.load(template_img)
img_shape = template_img.shape


# get the sum image's array
def image_sum(group, weeks,
              prefix, suffix,
              segment,
              shape = img_shape, lme_dir = lme_dir): # weeks is a subset of the images whose sum is being taken

    week_image = np.zeros(shape)

    # load images
    for w in weeks:
        img_path = f'{lme_dir}/{segment}/{group}_{prefix}_{w}_{suffix}.nii.gz'
        img = nib.load(img_path)
        img_arr = img.get_fdata()

        # add each image to the ohterall image
        week_image += img_arr
    
    return week_image

def make_summed_img(group, weeks, segment, metric, shape = img_shape):
    """
    metric = 'beta' or 'bse' ONLY
    """

    the_prefix = f'MNISymC_{segment}'
    the_suffix = f'lme_{metric}'

    save_suffix = 'lme' if metric == 'beta' else 'lme_se'
    week_num = weeks[-1] # last element in weeks (list, str) is the week for which we are summing

    week_arr = image_sum(group = group, weeks = weeks, prefix = the_prefix, suffix = the_suffix, segment = segment, shape = shape)
    week_img = nib.Nifti1Image(week_arr, template_img.affine)

    # e.g. save_suffix = 'lme' or 'lme_se' (or lme_beta, lme_se respectively)
    nib.save(week_img, f'{lme_dir}/{segment}/{group}_{the_prefix}_{week_num}_{save_suffix}.nii.gz')


#%%

# MACROS
patients = 'patients'
controls = 'controls'

week0 = ['W0'] # week 0 image
week1 = ['W0', 'W4'] # week 1 image = week 0 + week 1
week2 = ['W0', 'W4', 'W12'] # week 2 image = week 0 + week 1 + week 2
week3 = ['W0', 'W4', 'W12', 'W24'] # ...
week4 = ['W0', 'W4', 'W12', 'W24', 'W52']
week_list = [week1, week2, week3, week4]

segments = ['T1', 'GM', 'WM', 'CSF']


beta_suffix = 'lme_beta'
bse_suffix = 'lme_bse'

save_beta = 'lme'
save_bse = 'lme_se'

#%%
# PATIENTS

# beta
for seg in segments:
    for w in week_list:
        make_summed_img(group = patients, weeks = w, segment = seg, metric = 'beta')
        print(f'image done for {seg} {w} beta patients')

# bse
for seg in segments:
    for w in week_list:
        make_summed_img(group = patients, weeks = w, segment = seg, metric = 'bse')
        print(f'image done for {seg} {w} bse patients')

#%%
# CONTROLS

# beta
for seg in segments:
    for w in week_list:
        make_summed_img(group = controls, weeks = w, segment = seg, metric = 'beta')
        print(f'image done for {seg} {w} beta controls')

# bse
for seg in segments:
    for w in week_list:
        make_summed_img(group = controls, weeks = w, segment = seg, metric = 'bse')
        print(f'image done for {seg} {w} bse controls')

