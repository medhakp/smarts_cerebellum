#%%
import numpy as np
import nibabel as nib
import os

import smarts_cerebellum.globals as gl


# get the sum of images - e.g. from lme, get the total voxel intensity for that week

lme_dir = os.path.join(gl.baseDir, 'lme')
prefix = 'MNISymC_T1'

#beta_name = 'MNISymC_T1_W0_lme_beta'

template_img = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'
template_img = nib.load(template_img)
img_shape = template_img.shape


# path to save images to
save_path = os.path.join(gl.baseDir, 'lme')

# e.g. shape = shape of template image (if in MNISymC, use template image for shape)


# get the sum image's array
def image_sum(group, weeks, shape, 
              suffix, lme_dir = lme_dir, prefix = prefix): # weeks is a subset of the images whose sum is being taken

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

#%%
# GET SUMMED IMAGES FOR EACH WEEK

# PATIENTS
group = 'patients'

# betas
beta_suffix = 'lme_beta'

# get week 1 image
week1_arr = image_sum(group = group, weeks = week1, shape = img_shape, suffix = beta_suffix)
week1_img = nib.Nifti1Image(week1_arr, template_img.affine)
nib.save(week1_img, f'{save_path}/{group}_{prefix}_W4_lme.nii.gz')

# get week 2 image
week2_arr = image_sum(group = group, weeks = week2, shape = img_shape, suffix = beta_suffix)
week2_img = nib.Nifti1Image(week2_arr, template_img.affine)
nib.save(week2_img,  f'{save_path}/{group}_{prefix}_W12_lme.nii.gz')

# get week 3 image
week3_arr = image_sum(group = group, weeks = week3, shape = img_shape, suffix = beta_suffix)
week3_img = nib.Nifti1Image(week3_arr, template_img.affine)
nib.save(week3_img,  f'{save_path}/{group}_{prefix}_W24_lme.nii.gz')

# get week 4 image
week4_arr = image_sum(group = group, weeks = week4, shape = img_shape, suffix = beta_suffix)
week4_img = nib.Nifti1Image(week4_arr, template_img.affine)
nib.save(week4_img,  f'{save_path}/{group}_{prefix}_W52_lme.nii.gz')

# bse
bse_suffix = 'lme_bse'

# get week 1 image
week1_arr = image_sum(group = group, weeks = week1, shape = img_shape, suffix = bse_suffix)
week1_img = nib.Nifti1Image(week1_arr, template_img.affine)
nib.save(week1_img, f'{save_path}/{group}_{prefix}_W4_lme_se.nii.gz')

# get week 2 image
week2_arr = image_sum(group = group, weeks = week2, shape = img_shape, suffix = bse_suffix)
week2_img = nib.Nifti1Image(week2_arr, template_img.affine)
nib.save(week2_img,  f'{save_path}/{group}_{prefix}_W12_lme_se.nii.gz')

# get week 3 image
week3_arr = image_sum(group = group, weeks = week3, shape = img_shape, suffix = bse_suffix)
week3_img = nib.Nifti1Image(week3_arr, template_img.affine)
nib.save(week3_img,  f'{save_path}/{group}_{prefix}_W24_lme_se.nii.gz')

# get week 4 image
week4_arr = image_sum(group = group, weeks = week4, shape = img_shape, suffix = bse_suffix)
week4_img = nib.Nifti1Image(week4_arr, template_img.affine)
nib.save(week4_img,  f'{save_path}/{group}_{prefix}_W52_lme_se.nii.gz')
# %%

# make summarized dataframe using anatomical atlas Diedrichsen_2009
import SUITPy as suit
import os
import smarts_cerebellum.globals as gl

save_path = os.path.join(gl.baseDir, 'lme')
all_weeks = ['W0', 'W4', 'W12', 'W24', 'W52']


# finds one file per week
def _image_paths(group, suffix, prefix, weeks = all_weeks):
    images = []
    for week in weeks:
        file = f'{save_path}/{group}_{prefix}_{week}_{suffix}.nii.gz'
        images.append(file)
    return images



# dataframe will just be: image, roi, (other atlas_summary cols), isPatient (add this one), week (add)

def summary_df(images, param, isPatient, the_atlas = 'Diedrichsen_2009', maps = 'atl_Anatom', space = 'MNISym'):
     suit.fetch_atlas(the_atlas)

     df = suit.summarize_data(images = images, atlas = the_atlas, maps = maps, space = space,
                              stats = ['mean', 'median', 'nansum']
                              )
     df['isPatient'] = isPatient # bool
     df['param'] = param # betas or bse?
     # save week somewhere...maybe we can search for the week in image_name? Or code it later from image (number in atlas)

     return df
#%%
# PATIENTS - summed betas and summed bse
group = 'patients'
prefix = 'MNISymC_T1'
suffix = 'lme'


patient_images = _image_paths(group = group, suffix = suffix, prefix = prefix)
patients_df = summary_df(images = patient_images, isPatient = 1)

# save betas_df, bse_df together
