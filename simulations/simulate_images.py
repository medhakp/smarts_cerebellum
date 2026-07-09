# for some reason, smarts_cerebellum isn't found without this
import sys
sys.path.append('/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/')

import numpy as np
import nibabel as nib
from pathlib import Path
import smarts_cerebellum.globals as gl


# template
template_img = '/home/UWO/mporwal2/Documents/GitHub/smarts_cerebellum/tpl-MNI152NLin2009cSymC_T1w.nii'
template_img = nib.load(template_img)

N_p = 10 # subjects
N_t = 5 # time points (number of)

np.random.seed(13) # make sure we get the same random numbers each time
voxels = np.random.rand(N_t,N_p) # 5 weeks, 10 subjects


def subj_images(N_t = N_t, N_p = N_p):
    all_matrices =[]
    for week in range(N_t): # week number
        # each week gets its own voxels
        w_voxels = voxels[week,:]
        for s in range(N_p): # subj number
            # each subject gets their own voxel (singular!) from the week_voxels array

            # empty matrix for each subj-week
            sw_matrix = np.zeros(template_img.shape)
            sw_matrix[1,::] = w_voxels[s]
            all_matrices.append(sw_matrix)
    return all_matrices

all_matrices = subj_images() # list of matrices; M matrices, M = num_subjs * num_weeks
# so the first N_p matrices in this list are each subject's W0 matrices; next N_p matrices are each subject's W1 matrices; etc.

def save_images(all_matrices = all_matrices, N_t = N_t, N_p = N_p):
    for t in range(N_t):
        week_matrices = all_matrices[10*t : 10*t + 10] # access 10 elts
        for subj in range(N_p):
            arr = week_matrices[subj] # get that subject's matrix from list of week matrices
            img = nib.Nifti1Image(arr, template_img.affine)
            subj_dir = Path(gl.baseDir)/'simulations'/f'subj{subj}'
            subj_dir.mkdir(parents = True, exist_ok = True)
            nib.save(img, f'{gl.baseDir}/simulations/subj{subj}/simulated_subj{subj}_W{t}.nii.gz')


save_images()