import nibabel as nib
import pandas as pd
from pathlib import Path
import os
import smarts_cerebellum.globals as gl

# flop slope images from regression

def FlipLR(image):
    """
    Simple flip: flips image along x-axis (L-R flip)

    Input: image (Nifti or string)

    Output: Nifti image
    """
    if type(image) == str:
        image = nib.load(image)
    
    img_arr = image.get_fdata()

    flip_LR = img_arr[::-1, :,:]

    flipped_img = nib.Nifti1Image(flip_LR, image.affine)
    
    return flipped_img

def flip_left_lesion(path, 
                     left_lesion_df, # e.g. from p_df, subjs with LesionSide == 'left '
                     space='MNISymC', 
                     segment='T1', 
                     metric='slope'):
    '''
    flip left lesion to the right
    '''

    for subj in left_lesion_df.subj_id.unique():
        flip = f'{path}/{subj}/{subj}_{space}_{segment}_{metric}.nii.gz'

        if not Path(flip).is_file():
            continue

        flipped = FlipLR(flip)

        nib.save(flipped, f'{path}/{subj}/{subj}_{space}_{segment}_{metric}_FlipLR.nii.gz')

if __name__=='__main__':
    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    left_lesion_df = p_df[p_df.LesionSide == 'left ']
    path = os.path.join(gl.baseDir, 'regression')

    segments = ['T1', 'WM', 'GM', 'CSF']
    for segment in segments:
        flip_left_lesion(path, left_lesion_df, segment = segment, metric = 'slope')