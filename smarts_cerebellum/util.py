"""
This utils file contains calls for functions available in smarts_cerebellum, and helper functions for those functions.
"""

import numpy as np
import pandas as pd

import re
import nibabel as nib
from pathlib import Path
import SUITPy as suit

# smarts_cerebellum functions
from smarts_cerebellum import mirror_lesion
from smarts_cerebellum import regression

# base directory for project, participants tsv
import smarts_cerebellum.globals as gl
base_dir = gl.baseDir
p_df = pd.read_csv(f'{base_dir}/participants_anat.tsv', sep = '\t')

"""
Make this a general function call: the only part that is specific to MNISym_coreg is the path name, so have a general path name.
Then, when we call it in MNISym_coreg_regression pipeline, we can just have the path defined before we call the function, and have an insertable "type".
"""
def subj_unique_regression_week(subdir, suffix):

    """
    General call for regression function (voxel-wise regression on each subject's weeks).
    Saves intercept and slope images to specified path inside smarts_cerebellum/Regression/{subj} for each subject

    Input:
        type (str): type of image; used for finding image and for saving images
            valid types: GM, WM, T1, CSF
        subdir (str): directory containing subject folders inside smarts_cerebellum
        suffix (str): image suffix

        (Image path follows structure: smarts_cerebellum/{subdir}/{subj}/{subj}_{refT1}_{suffix}.nii.gz)
        Image saved:
            folder: smarts_cerebellum/Regression/{subj}
            image_name: {subj}_{suffix}_{intercept/slope}

    **If getting error "path not exist", uncomment the line to make results_path**
    This assumes that the results path (smarts_cerebellum/Regression/subj) exists

    """

    for subj in p_df['subj_id'].unique():

        # find each subject's reference image, and run it through the regression
        refT1 = (p_df.loc[(p_df['subj_id']==subj), 'RefT1'].iloc[0]).strip()
        ref_img = f'{base_dir}/{subdir}/{subj}/{subj}_{refT1}_{suffix}.nii.gz'

        print(f"Regression on {subj} \n")

        intercept_img, slope_img = regression.perform_regression_week(subj_id = subj,
                            reference_img = ref_img
                            )
        

        # if images exist, save them
        if intercept_img is not None and slope_img is not None:
            #results_path = f'{base_dir}/Regression/{subj}'
            
            results_path = f'{base_dir}/regression_test/{subj}'
            
            results_path = Path(results_path)

            # comment this out if this directory already exists
            #results_path.mkdir(parents = True, exist_ok = True)

            nib.save(intercept_img, f'{results_path}/{subj}_{suffix}_intercept.nii.gz')
            nib.save(slope_img, f'{results_path}/{subj}_{suffix}_slope.nii.gz')


# PERHAPS THIS PART CAN JUST BE THE CALL FOR THE MAKE DF FCN THAT ALREADY EXISTS?
# BUT THAT FUNCTION CAN PROBABLY BE CALLED AS-IS

# def _assemble_dataframe(atlas_df, p_df, subj):
#     """
#     Creates a descriptive dataframe
#     UNIQUE SUBJECT IMAGE, NOT WEEKS! --> weeks under construction!

#     Inputs:
#         atlas_df (Pandas dataframe): dataframe from atlas summary
#         p_info (Pandas dataframe): dataframe with descriptive information for participants

#     Outputs:
#         atlas_df (Pandas dataframe): updated dataframe (with descriptive information)
#     """

#     # try doing this for only one subject; then, we can loop through in the call
#     refT1 = p_df[p_df.subj_id == subj]['RefT1'].iloc[0].strip()
#     subj_df = p_df[(p_df.subj_id == subj) & (p_df.Week.str.strip() == refT1)]


#     # mask the row to which we are adding data
#     row_mask = (atlas_df.subj_id == subj)
#     print(f'Writing data for {subj}')

#     atlas_df.loc[row_mask, 'ID'] = subj_df['ID'].values[0]
#     atlas_df.loc[row_mask, 'Centre'] = subj_df['Centre'].values[0]
#     atlas_df.loc[row_mask, 'RefT1'] = refT1
#     atlas_df.loc[row_mask, 'age'] = subj_df['age'].values[0]
#     atlas_df.loc[row_mask, 'Gender'] = subj_df.Gender.values[0]
#     atlas_df.loc[row_mask, 'isPatient'] = subj_df.isPatient.values[0]
#     atlas_df.loc[row_mask, 'LesionSide'] = subj_df.LesionSide.values[0]
#     atlas_df.loc[row_mask, 'LesionLocation'] = subj_df.LesionLocation.values[0]
#     atlas_df.loc[row_mask, 'handedness'] = subj_df.handedness.values[0]
 
#     return atlas_df


# # Make summarized dataframe
# def make_summarized_dataframe(p_df,
#                               search_path,
#                               the_atlas, maps, space,
#                               ):
#     """
#     Make full summarized dataframe that has: ROIs for each subject, along with descriptive information

#     Inputs:
#         p_df (Pandas dataframe): info file for participants
#         search_path (str): directory where files are stored (parent directory for all subjects)
#         suffixes (tuple of str): suffixes for all files you want to find

#         the_atlas (str): cerebellar atlas --> see SUITPy
#         maps (str): map to use in summarizing (cerebellar map) --> see SUITPy
#         space: space of the files


#     Outputs:

#     """

#     suffixes = [
#     'MNISym_CSF_coreg_reslice_slope.nii.gz',
#     'MNISym_logJac_coreg_reslice_slope.nii.gz',
#     'MNISym_WM_coreg_reslice_slope.nii.gz',
#     'MNISym_GM_coreg_reslice_slope.nii.gz',
#     'MNISym_T1_coreg_reslice_slope.nii.gz'
#     ]

#     flipped_suffixes = [
#         'MNISym_CSF_coreg_reslice_slope_FlipLR.nii.gz',
#         'MNISym_logJac_coreg_reslice_slope_FlipLR.nii.gz',
#         'MNISym_WM_coreg_reslice_slope_FlipLR.nii.gz',
#         'MNISym_GM_coreg_reslice_slope_FlipLR.nii.gz',
#         'MNISym_T1_coreg_reslice_slope_FlipLR.nii.gz'
#     ]

#     dfs = []

#     left_lesion_df = p_df[p_df.LesionSide == 'left ']

#     # loop through all subjects - perform each operation on each subject
#     for subj in p_df.subj_id.unique():
#         # find their files - returns string list of files
#         if subj in left_lesion_df.subj_id.unique():
#             file_list = file_search(search_path = search_path, subj_id = subj, suffixes = flipped_suffixes)
#         else:
#             file_list = file_search(search_path = search_path, subj_id = subj, suffixes = suffixes)
        
#         if not file_list:
#             continue # skip subjects without the files
        
#         # summarize volume in each ROI for each file type
#         suit.fetch_atlas(the_atlas)
#         df = suit.summarize_data(images = file_list,
#                                  atlas = the_atlas,
#                                  maps = maps,
#                                  space = space,
#                                  stats = ['mean', 'median', 'nansum'])
        
#         df['subj_id']= subj

#         # then make the descriptive dataframe for each subject
#         descriptive_df = _assemble_dataframe(atlas_df = df, p_df = p_df, subj = subj)

#         # add all dataframes to the list
#         dfs.append(descriptive_df)

#     # combine all of them
#     all_df = pd.concat(dfs, ignore_index = True)

#     return all_df


def flip_left_lesion(path, left_lesion_df, suffix):
    '''
    flip left lesion to the right
    
    Inputs:
        path (str): base path to subject files
            image will be found in: f'{path}/{subj}/{subj}_{suffix}.nii.gz'
        left_lesion_df (Pandas dataframe): dataframe containing all participants with left hemisphere lesion - to be flipped!
        suffix (str): image suffix (for image to be flipped)

        Filenames follow convention {subj}_{suffix}.nii.gz
        Output images saved as {subj}_{suffix}_FlipLR.nii.gz
        File path follows convention {path}/{subj}/{file_name}
    
    Image is saved to the directory where the original image is found;
        same name, with 'FlipLR' appended to the name
    '''
    
    # use the flip function available as its own .py file?
    # def _FlipLR(image):
    #     """
    #     Simple flip: flips image along x-axis (L-R flip)

    #     Input: image (Nifti or string)

    #     Output: Nifti image
    #     """
    #     if type(image) == str:
    #         image = nib.load(image)
        
    #     img_arr = image.get_fdata()

    #     flip_LR = img_arr[::-1, :,:]

    #     flipped_img = nib.Nifti1Image(flip_LR, image.affine)
        
    #     return flipped_img


    for subj in left_lesion_df.subj_id.unique():
        flip_image = f'{path}/{subj}/{subj}_{suffix}.nii.gz'

        # check if file exists
        if not Path(flip_image).is_file():
            print(f'Skip {subj}')
            continue

        # flip image along x-axis (flips left-lesion image to right)
        flipped = mirror_lesion.FlipLR(flip_image)
        
        # save image to specified directory for each subject with 'FlipLR' appended to the end of its name
        nib.save(flipped, f'{path}/{subj}/{subj}_{suffix}_FlipLR.nii.gz')


# HELPER FUNCTIONS
#_____________________________________________________________

# def find_weeks(SID):

#     # @Marco
    
#     ### look into particpants.tsv and return weeks as numpy array of int e.g., (2, 4, )
    
#     p_df = pd.read_csv('/cifs/diedrichsen/data/smarts_cerebellum/participants_anat.tsv', sep = '\t')

#     # access only that subject's rows
#     df_subj = p_df[p_df.subj_id == SID]
#     weeks = []

#     for week in df_subj['week']:
#         weeks.append(week)

#     return weeks


# def week_path_search(reference_file, subj_id):
#     """
#     Finds files from other weeks that match the structure of reference file.

#     Inputs:
#         reference_file (str): path to a file whose path will be used as reference.
#             That is, this file's path should have the structure that all other files from that week should have.
#         weeks: weeks in filepath
    
#     Outputs:
#         week_paths (list[str]): paths to all files (including reference) that exist for weeks
#         week_available (list[str]): weeks whose files exist
#     """

#     ref_path = str(reference_file)

#     # find all places in path str with the week
#     match = re.search(r'W(\d+)', ref_path)
#     if not match:
#         print(f'could not find week token in reference path for {ref_path}')
#         return None
    
#     ref_week_token = match.group(1) # return entire text that ws matched.

#     weeks_paths = []
#     weeks_available = []

#     weeks = find_weeks(subj_id)

#     for week in weeks:
#         # search for every week's file

#         # replace the week token(s) in reference image path with other tokens for new week path
#         #week_path = ref_path.replace(ref_week_token, f'W{week}')

#         week_path = re.sub(rf'W{ref_week_token}(?!\d)', f'W{week}', ref_path)

#         # this should be dead code
#         if not Path(week_path).exists():
#             print(f'skipping W{week}')
#             continue

#         weeks_paths.append(week_path)
#         weeks_available.append(week) # add weeks as integers

#     return weeks_paths, weeks_available

# def file_search(search_path, subj_id, suffixes):
#     """
#     Function to search for all files for a given subject with specified suffixes.
#     Also checks if files exist - only returns those that exist.

#     Inputs:
#         search_path (str): base path to search for files in
#         subj_id (str): subject whose file(s) to search for - searches in their directory
#         suffixes (tuple of str): suffixes of files; include extension (i.e. .nii or .nii.gz extensions)
#         # (TBA) week (str): if subject files are stored by weeks
    
#     Outputs:
#         file_list (tuple of str): list of files for that subject
#     """

#     file_list = []

#     for suffix in suffixes:
#         file_path = f'{search_path}/{subj_id}/{subj_id}_{suffix}'

#         if not Path(file_path).is_file():
#             #print(f'Path {file_path} not found; skipping')
#             continue

#         file_list.append(file_path)
    
#     return file_list

# #__________________________