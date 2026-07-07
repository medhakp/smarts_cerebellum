#%%
import numpy as np
import nibabel as nib
import os

import smarts_cerebellum.globals as gl
# get the sum of images - e.g. from lme, get the total voxel intensity for that week

lme_dir = os.path.join(gl.baseDir, 'lme')
prefix = 'MNISymC_T1'
suffix = 'lme_beta'
#beta_name = 'MNISymC_T1_W0_lme_beta'

template_img = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'
template_img = nib.load(template_img)
img_shape = template_img.shape


# path to save images to
save_path = os.path.join(gl.baseDir, 'lme')

# e.g. shape = shape of template image (if in MNISymC, use template image for shape)


# get the sum image's array
def image_sum(group, weeks, shape, 
              lme_dir = lme_dir, prefix = prefix, suffix = suffix): # weeks is a subset of the images whose sum is being taken

    week_image = np.zeros(shape)

    # load images
    for w in weeks:
        img_path = f'{lme_dir}/{group}_{prefix}_{w}_{suffix}.nii.gz'
        img = nib.load(img_path)
        img_arr = img.get_fdata()

        # add each image to the ohterall image
        week_image += img_arr
    
    return week_image


week0 = ['W0'] # week 0 image
week1 = ['W0', 'W4'] # week 1 image = week 0 + week 1
week2 = ['W0', 'W4', 'W12'] # week 2 image = week 0 + week 1 + week 2
week3 = ['W0', 'W4', 'W12', 'W24'] # ...
week4 = ['W0', 'W4', 'W12', 'W24', 'W52']


# PATIENTS
group = 'patients'

# get week 1 image
week1_arr = image_sum(group = group, weeks = week1, shape = img_shape)
week1_img = nib.Nifti1Image(week1_arr, template_img.affine)
nib.save(week1_img, f'{save_path}/{group}_{prefix}_W4_lme.nii.gz')

# get week 2 image
week2_arr = image_sum(group = group, weeks = week2, shape = img_shape)
week2_img = nib.Nifti1Image(week2_arr, template_img.affine)
nib.save(week2_img,  f'{save_path}/{group}_{prefix}_W12_lme.nii.gz')

# get week 3 image
week3_arr = image_sum(group = group, weeks = week3, shape = img_shape)
week3_img = nib.Nifti1Image(week3_arr, template_img.affine)
nib.save(week3_img,  f'{save_path}/{group}_{prefix}_W24_lme.nii.gz')

# get week 4 image
week4_arr = image_sum(group = group, weeks = week4, shape = img_shape)
week4_img = nib.Nifti1Image(week4_arr, template_img.affine)
nib.save(week4_img,  f'{save_path}/{group}_{prefix}_W52_lme.nii.gz')
# %%
