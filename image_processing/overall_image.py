import numpy as np
import pandas as pd
import nitools as nt
import nibabel as nib

"""
Get the overall image for a series of images. For example, average slope in MNISym space.
"""

base_dir = '/cifs/diedrichsen/data/smarts_cerebellum'
p_df = pd.read_csv('/cifs/diedrichsen/data/smarts_cerebellum/participants_anat.tsv', sep = '\t')


def get_world_coordinates(image_path):
    """
    Function to get world coordinates of an image (given its voxel coordinate array).

    Inputs:
        image_path (str): path to image
    Output:
        world_array (Numpy array)
    """
    image = nib.load(image_path)

    affine = image.affine
    voxel_array = image.get_fdata()

    i, j, k = np.meshgrid(voxel_array.shape, indexing = 'ij')

    x,y,z = nt.affine_transform(i, j, k, affine)

    # resample the image into world coordinates
    world_array = nt.sample_image(image,
                                  xm = x, ym = y, zm = z,
                                  interpolation = 1)
    
    return world_array


def subj_unique_world_coords(p_df, suffix):
    """
    Loops through all subjects in participants dataframe, finds images, performs some function
    
    Inputs:
        p_df: participants dataframe to read from (to find subjects)
        suffix: image suffix, where input images follow format '{subj}_{suffix}.nii.gz'
    Output:
        world_arrs (tuple of numpy arrays): world coordinate arrays for all subject images
    """

    world_arrs = []
    for subj in p_df['subj_id'].unique():
        # for each subject, find their slope image for type given by suffix
        subj_slope = f'{base_dir}/Regression/{subj}/{subj}_{suffix}.nii.gz'

        subj_world_arr = get_world_coordinates(subj_slope)

        world_arrs.append(subj_world_arr)

    return world_arrs


def average_image(affine, suffix):
    """
    Function to get overall image

    Inputs:
        affine (np.array): affine with which to write resultant image
        suffix (str): suffix of images being read, such that files follow naming convention '{subj}_{suffix}.nii.gz;
            e.g. suffix = 'MNISym_GM_coreg_reslice_slope'

    Output:
        result_image (Nifti1Image): average image
    """

    # get all image arrays
    world_arrays = subj_unique_world_coords(suffix = suffix)

    # get mean of all arrays
    result = np.mean(world_arrays, axis = 0) # np array (tensor)

    # write image back to Nifti
    result_image = nib.Nifti1Image(result, affine)

    return result_image