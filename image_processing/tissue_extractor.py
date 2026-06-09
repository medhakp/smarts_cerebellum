# fix documentation; INSTALL NEWEST VERSION OF SUITPy FROM MASTER BRANCH IN THE VIRTUAL ENV

# too many inputs for each function; take out.
# don't put in directories or path; take out
# have option for results path, default is None or smth; default saves to same dir as notebook
# reslice function: option to take path (load as nifti with nib) or nifti; change return output to Posixpath

"""
fixes

- not hardcode directories
- Reslice function
- add summarize.tsv function (helper function)
- template volume function - outputs summarized using helper function
- ROI volume function - uses helper summarize.tsv function
- function to loop over participants information file.
- documentation for each function.
"""

"""
Using the SUITPy pipeline (https://github.com/DiedrichsenLab/SUITPy), extracts the volume of a over specified atlas ROIs or for the whole template.
"""

# Imports
from nilearn import plotting as npl
import nibabel as nib
import ants
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import SUITPy as suit
import SUITPy.atlas as atlas

#import tissue_extractor as te

from pathlib import Path


# specify tissue in function call
#tissue = 'wm' # default
tissue_dict = {
    'gm': 'c1',
    'wm': 'c2',
    'csf': 'c3'
}

# directories
anat_dir = '/cifs/diedrichsen/data/smarts_cerebellum/anatomicals'
p_df = pd.read_csv('/cifs/diedrichsen/data/smarts_cerebellum/participants_anat.tsv', sep = '\t')

# 1. SUITPy isolation
"""
Isolate cerebellum from anatomical
Input: t1-weighted anatomical
Output: cerebellar isolation mask
"""

def isolate(t1_path, subj_id, week, results_path):
    mask = suit.isolate(t1_path, result_folder = results_path, verbose = 1)
    mask_path = Path(results_path)/f'{subj_id}_{week}_T1_cerebellum_dseg.nii.gz' # path to the mask

    return mask_path


# 2. SUITPy normalization
"""
Normalize T1w anatomical in native space to SUIT (or other) space
Inputs:
    T1w anatomical
    cerebellar isolation mask (from `suit.isolate`)
Outputs:
    Returns a dictionary with several files, including optional outputs:
        (log) Jacobian determinant: change in voxel sizes
        fwd_transforms: transformation file for native to SUIT space
"""

def normalize(t1_path, mask_path, results_path): # fix: make option to choose which files are written
    results = suit.normalize(
        source_file = t1_path,
        mask_file = str(mask_path),
        space = 'SUIT',

        # optional files
        write_jacobian_determinant = True,
        write_log_jacobian_determinant = True, #if log_jac == True else False, 
        write_ants_transform = False,
        write_normalized = True,
        write_inv_deformation = True,

        results_folder = results_path,

        verbose = 1
    )

    return results


# 3. SUITPy reslice image
"""
Reslice image from a given space to another (e.g. forward: native to SUIT space)
Inputs:
    tissue segmentation file 
        - (e.g. c1 file)
        - tissue volume (e.g. grey matter volume)
    deformation image: from normalization module (transformation file)
        If native --> template, use forward deformation

    cerebellar isolation mask (optional)
        - use if interested in cerebellum
Output:
    - resliced image: tissue in SUIT space
    - probability of tissue in space
"""

def reslice(tissue_path, fwd_def,  mask_path,
            results_path, subj_id, week, tissue):
    resliced_img = suit.reslice_image(source_image = tissue_path,
                                      deformation = fwd_def,
                                      mask = str(mask_path)
                                      )
    nib.save(resliced_img, Path(results_path)/f'{subj_id}_{week}_T1_{tissue}_resliced.nii.gz')

    resliced_img_path = f'{results_path}/{subj_id}_{week}_T1_{tissue}_resliced.nii.gz'
    return resliced_img_path

# IS THIS VOLUME IMAGE REALLY NECESSARY? or correct?


# Modulated tissue volume image
"""
    To calculate volume:
    (for regions) average the detJ volume per region and multiply it by the volume of the region in template space (estimates volume in native space)
    (for template) voxel-wise approach: multiply detJ image (each voxel) by voxel size (volume of each voxel in template)
        Approximates tissue volume in native space
        This is equivalent to region-wise approach where each voxel is treated as its own region
        To get the total volume, sum over all the voxels.
    """

"""
Calculates tissue volume in template space (per voxel); returns tissue volume image in template space.
"""
# either rename this function to voxelwise_volume_img or also return the volume
def voxelwise_volume(
        resliced_img,
        jac_det,
        log_jac_det, # fix: choose jac det or log
        tissue, # fix: option to not have tissue
        subj_id, 
        week, 
        results_path):
    
    """
    ...documentation...

    Returns volume image as a Nifti image.
    Talk about how to get tissue volume by-voxel
    If you want tissue volume, use resliced tissue image
    """

    if type(resliced_img) == str:
        resliced_img = nib.load(resliced_img)

    if type(jac_det) == str:
        jac_det = nib.load(jac_det)

    resliced_arr = resliced_img.get_fdata()
    jac_det_arr = jac_det.get_fdata()

    # tissue volume
    volume = resliced_arr*jac_det_arr

    # save volume image with same affine + header
    volume_img = nib.Nifti1Image(volume, resliced_img.affine, resliced_img.header)

    # maybe can take this out, reduce function inputs.
    nib.save(volume_img, f'{results_path}/{subj_id}_{week}_T1_{tissue}_vol.nii.gz')

    # return as nifti img
    return volume_img


# Atlas summary
"""
summarize volumes with atlas-based ROIs
"""
def atlas_summ(tissue_vol_img, atlas, maps, space = 'SUIT'): # fix: make region-wise volume function (that can be called in this)
    # need to update method for calculating volume based on tutorial: https://github.com/DiedrichsenLab/SUITPy/blob/develop/docs/source/tutorials/2.quickstart_anatomical.ipynb

    df = suit.summarize_data(
        images = tissue_vol_img, # [detJ_file]
        atlas = atlas,
        maps = maps,
        space = 'SUIT',
        stats = ['mean']

    )

    # region-wise volume
    df['ind_vol'] = df['mean']*df['volume'] # region-wise volume (approximated in individual space)

    return df

# Make summarized dataframe
"""
summarized dataframe; default as .tsv
"""

"""
tissue = 'wm'
tissue_dict = {
    'gm': 'c1',
    'wm': 'c2',
    'csf': 'c3'
}

# possibly make this into a function and edit loop (since we have subj_id in the .tsv file now)
for i in range(0, p_df.shape[0]):
    p_id = p_df['ID'].iloc[i]
    week = (p_df['Week'].iloc[i]).strip() # sometimes have extra white spaces
    p_centre = (str(p_df['Centre'].iloc[i])).strip()
    refT1 = (p_df['RefT1'].iloc[i]).strip()

    subj_id = f'{p_centre.strip()}_{p_id}'

    iso_norm_dir = f'{anat_dir}/{subj_id}/{week}/iso_norm/'
    #t1_path = f'{anat_dir}/{subj_id}/{week}/{subj_id}_{week}_T1.nii'
    tissue_path = f'{anat_dir}/{subj_id}/{week}/{tissue_dict[tissue]}{subj_id}_{week}_T1.nii'
    fwd_def = f'{iso_norm_dir}/{subj_id}_{week}_T1_to-SUIT_mode-image_xfm.nii.gz'
    mask_path = f'{iso_norm_dir}/{subj_id}_{week}_T1_cerebellum_dseg.nii.gz'
    jac_det = f'{iso_norm_dir}/{subj_id}_{week}_T1_to-SUIT_mode-image_detJ.nii.gz'
    resliced_img = f'{anat_dir}/{subj_id}/{week}/{tissue}_results/{subj_id}_{week}_T1_tissue_resliced.nii'

    # check that paths exist
    if not Path(tissue_path).is_file():
        print(f'{tissue} path does not exist for {subj_id} in week {week}')
        continue

    # make a new folder inside subject's week folder for results
    results_path = Path(anat_dir)/subj_id/week/f'{tissue}_results'
    results_path.mkdir(parents=True, exist_ok = True) # exist_ok = True

    # summarize volume in ROIs - THIS PART SHOULD BE FCN IN TE; ADD IT
    suit.atlas.fetch_atlas('Diedrichsen_2009')
    df = suit.summarize_data(
        images = [resliced_img],
        atlas  = 'Diedrichsen_2009',
        maps   = 'atl-Anatom',
        space  = 'SUIT',
        stats  = ['mean', 'nansum'])
    
    df['ind_vol'] = df['mean']*df['volume']
    df.rename(columns={'mean': f'avg_{tissue}v'}, inplace = True)
    df['image_name'] = f'{tissue}v_img_{subj_id}_{week}_T1.nii'
    df['subj_id'] = subj_id
    df['Week'] = week


    # put all of this in a new dataframe
    if i == 0:
        # header for only the first run
        all_df = df
    else:
        all_df = pd.concat([all_df, df], ignore_index = True) # all_df already exists, so all good

    row_mask = (all_df['subj_id']==subj_id) & (all_df['week']==week)
    print(f'Writing data for {subj_id} at {week}')

    all_df.loc[row_mask, 'ID'] = p_id
    #all_df.loc[row_mask, 'Week'] = week
    all_df.loc[row_mask, 'week'] = str(p_df['week']).iloc[i] # numeric week value so we don't hve to do it later
    all_df.loc[row_mask, 'Centre'] = p_centre
    all_df.loc[row_mask, 'RefT1'] = refT1
    all_df.loc[row_mask, 'age'] = str(p_df['age'].iloc[i])
    all_df.loc[row_mask, 'Gender'] = p_df['Gender'].iloc[i]
    all_df.loc[row_mask, 'isPatient'] = str(p_df['isPatient'].iloc[i])
    all_df.loc[row_mask, 'LesionSide'] = p_df['LesionSide'].iloc[i]
    all_df.loc[row_mask, 'LesionLocation'] = p_df['LesionLocation'].iloc[i]
    all_df.loc[row_mask, 'handedness'] = str(p_df['handedness'].iloc[i])

all_df.to_csv(f'{base_dir}/{tissue}v_total_atlas_summarized.tsv', mode = 'w', sep = '\t', index = False, header = True)
"""
