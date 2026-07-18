import nibabel as nib
import os
import numpy as np

import smarts_cerebellum.globals as gl
from smarts_cerebellum.util import subj_path_search

def make_week_dicts(df,
                    ref_subj,
                    subdir,
                    file_suffix,
                    weeks
                    ):

    dictionaries = []
    for week in weeks:
        ref_search_path = os.path.join(gl.baseDir, subdir, ref_subj, f'{ref_subj}_W{week}_{file_suffix}')
        paths, subjs = subj_path_search(ref_search_path, ref_subj, week, df)
        dictionaries.append(dict(zip(subjs, paths)))
    return dictionaries

# then: for each dictionary in the list, get a list of the paths available and pass this into image_sum function

def overall_img(image_paths, shape, metric):
    """
    metric = 'mean' or 'sum'
    """

    week_image = np.zeros(shape) # store summed image array
    counter = 0

    for path in image_paths:
        img = nib.load(path)
        img_arr = img.get_fdata()

        week_image += img_arr
        counter +=1
    
    if metric == 'mean':
        week_image = week_image / counter
        print('mean')
        return week_image
    else:
        return week_image



#subj_path_dict = make_week_dicts(df, ref_subj, subdir, file_suffix, timepoints)

# get file paths for each week (each dictionary in the list) and run image_sum

def week_images(prefix, suffix, save_dir, subj_path_dict, weeks, template, metric):

    for idx, w in enumerate(weeks):
        week_dict = subj_path_dict[idx]
        image_paths = list(week_dict.values())

        week_arr = overall_img(image_paths, template.shape, metric = metric)

        week_image = nib.Nifti1Image(week_arr, template.affine)

        # save images
        nib.save(week_image, f'{save_dir}/{prefix}_{w}_{suffix}.nii.gz')

        # save images with name: {prefix}_{week}_{suffix}.nii.gz
        # e.g. for controls average image: controls_MNISymC_{segment}_{week}_mean.nii.gz