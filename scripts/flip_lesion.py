import nibabel as nib
import pandas as pd
from pathlib import Path
import os
import smarts_cerebellum.globals as gl

def FlipLR(image):
    """
    Simple flip: flips image along x-axis (L-R flip)
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
                     metric='_slope',
                     use_weeks = False,
                     week_on_path = False):
    '''
    flip left lesion to the right
    '''
    flips = []
    for subj in left_lesion_df.subj_id.unique():
        if use_weeks == False:
       
            flip = f'{path}/{subj}/{subj}_{space}_{segment}{metric}.nii.gz'

            if not Path(flip).is_file():
                continue
            flips.append(flip)

            flipped = FlipLR(flip)

            nib.save(flipped, f'{path}/{subj}/{subj}_{space}_{segment}{metric}_FlipLR.nii.gz')
        
        else: # use_weeks == True
            # get all their weeks
            subj_df = left_lesion_df[left_lesion_df.subj_id == subj]
            weeks = subj_df.Week.unique()

            for _week in weeks:
                week = _week.strip()

                if week_on_path == True:
                    flip = f'{path}/{subj}/{week}/{subj}_{week}_{space}_{segment}{metric}.nii.gz'
                else:
                    flip = f'{path}/{subj}/{subj}_{week}_{space}_{segment}{metric}.nii.gz'
                
                if not Path(flip).is_file():
                    continue
                                
                flipped = FlipLR(flip)
                
                if week_on_path == True:
                    nib.save(flipped, f'{path}/{subj}/{week}/{subj}_{week}_{space}_{segment}{metric}_FlipLR.nii.gz')
                else:
                    nib.save(flipped, f'{path}/{subj}/{subj}_{week}_{space}_{segment}{metric}_FlipLR.nii.gz')

def flip_regression_slopes(left_lesion_df):
    path = os.path.join(gl.baseDir, 'regression')
    segments = ['T1', 'WM_mod', 'GM_mod', 'CSF_mod'] # ran regression on modulated tissue volumes
    for segment in segments:
        flip_left_lesion(path, left_lesion_df, segment = segment, metric = '_slope')

def flip_normalized_images(left_lesion_df, metric = '_mod'):
    # flip normalized segment images
    space = 'MNISymC'
    segments = ['WM', 'GM', 'CSF']
    for segment in segments:
        seg_path = os.path.join(gl.baseDir, f'{space}_{segment}')
        flip_left_lesion(seg_path, left_lesion_df, segment = segment, metric = metric, use_weeks = True)
    

    # flip normalized T1 images
    t1_path = os.path.join(gl.baseDir, f'{space}_T1')
    flip_left_lesion(t1_path, left_lesion_df, segment = 'T1', metric = '', use_weeks = True)

def flip_FaMap(left_lesion_df):
    path = os.path.join(gl.baseDir, 'MNISymC_FaMap')

    flip_left_lesion(path = path, left_lesion_df = left_lesion_df, segment = 'FaMap', metric = '', use_weeks = True)

def flip_detJ(left_lesion_df):
    path = os.path.join(gl.baseDir, 'MNISymC_trans')
    flip_left_lesion(path = path, left_lesion_df = left_lesion_df, space = 'T1', segment = 'to-MNI152NLin2009cSymC_mode-image_detJ', 
                     metric = '', use_weeks = True, week_on_path = True)
    


if __name__=='__main__':
    # for T1 anatomcials (regression slopes; normalized segment images; normalized T1 images)
    # for FaMap images: if they don't have an anatomical (T1), then subj cannot be normalized to template; so only worry about those with T1 AND Fa

    p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
    left_lesion_df = p_df[p_df.LesionSide == 'left ']
    
    flip_normalized_images(left_lesion_df, metric = '')
    
