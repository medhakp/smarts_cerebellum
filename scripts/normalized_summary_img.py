import pandas as pd
import nibabel as nib
import os
import re
import SUITPy as suit
import smarts_cerebellum.globals as gl
from smarts_cerebellum import summary_img as si

# MACROS
template_path = os.path.join(gl.baseDir, 'ROI', 'tpl-MNI152NLin2009cSymC_T1w.nii')
template_img = nib.load(template_path)

# EXCLUDING SOME SUBJS
p_df = pd.read_csv(os.path.join(gl.baseDir, 'participants.tsv'), sep = '\t')
p_df = p_df[~p_df.subj_id.isin(gl.bad)]

left_lesion_df = p_df[p_df.LesionSide == 'left ']

patients_df = p_df[p_df.isPatient == 1]
controls_df = p_df[p_df.isPatient == 0]

space = 'MNISymC'
segments = ['WM', 'GM', 'CSF']
weeks = ['W0', 'W4', 'W12', 'W24', 'W52']


# only need to run this once for each segment - just the (mean/median) image for each week

# for segment in segments:
#     seg_dir = f'{space}_{segment}'
#     for week in weeks:
#         si.mean_image_right(group = 'patients',
#                             group_df = patients_df,
#                             left_lesion_df = left_lesion_df,
#                             template_img = template_img,
#                             search_dir = seg_dir,
#                             segment = segment,
#                             metric = '_mod',
#                             week = week)
        
#         si.mean_image_right(group = 'controls',
#                             group_df = controls_df,
#                             left_lesion_df = left_lesion_df,
#                             template_img = template_img,
#                             search_dir = seg_dir,
#                             segment = segment,
#                             metric = '_mod',
#                             week = week)

# t1_dir = f'{space}_T1'
# for week in weeks:
#     si.mean_image_right(group = 'patients',
#                             group_df = patients_df,
#                             left_lesion_df = left_lesion_df,
#                             template_img = template_img,
#                             search_dir = t1_dir,
#                             segment = 'T1',
#                             metric = '',
#                             week = week)
#     si.mean_image_right(group = 'controls',
#                             group_df = controls_df,
#                             left_lesion_df = left_lesion_df,
#                             template_img = template_img,
#                             search_dir = t1_dir,
#                             segment = 'T1',
#                             metric = '',
#                             week = week)



# summarize inside dataframe
# images are just mean images, not subject-specific, but week-specific

def _week_token(image_name):
    match = re.search(r'W(\d+)', image_name)
    week_val = match.group(1)
    return week_val


def summarize_weeks(weeks = weeks,
                    group = None,
                    space = 'MNISymC',
                    segment = 'T1',
                    search_dir = None,
                    stats = ['mean'],
                    label_image = None,
                    region_names = None,
                    rois = None,
                    atlas_space = 'MNISymC',
                    atlas = None,
                    maps = None,
                    param = 'mean'
                    ):
    
    segment_images = []
    for week in weeks:
        fname = f'{group}_{week}_{space}_{segment}_{param}.nii'
        week_path = os.path.join(gl.baseDir, search_dir, fname)
        segment_images.append(week_path)

    if not atlas == None:
        suit.fetch_atlas(atlas)
    df = suit.summarize_data(images = segment_images,
                                     space = atlas_space,
                                     stats = stats,
                                     atlas = atlas,
                                     maps = maps,
                                     label_image = label_image,
                                     region_names = region_names)
    df['segment'] = segment
    df['Week'] = df['image_name'].apply(_week_token)
    df.to_csv(os.path.join(gl.baseDir, search_dir, f'summary_{group}_{space}_{rois}_{segment}_{param}.tsv'), sep='\t', index=False)

# custom map
roi_tract = 'CST'
label_image=os.path.join(gl.baseDir, 'ROI', f'MNISymC.{roi_tract}.nii')
region_names=[''] * 13 + [f'left_{roi_tract}', f'right_{roi_tract}']

# cerebellar atlas available from SUIT
atlas = 'Diedrichsen_2009'
maps = 'atl-Anatom'


for segment in segments:
    search_dir = f'MNISymC_{segment}/means'
    summarize_weeks(group = 'patients', segment = f'{segment}_mod', search_dir = search_dir, atlas_space = 'MNISym', atlas = atlas, maps = maps, rois = atlas)
    summarize_weeks(group = 'controls', segment = f'{segment}_mod', search_dir = search_dir, atlas_space = 'MNISym', atlas = atlas, maps = maps, rois = atlas)

    

summarize_weeks(group = 'patients', search_dir = 'MNISymC_T1/means', atlas_space = 'MNISym', atlas = atlas, maps = maps, rois = atlas)
summarize_weeks(group = 'controls', search_dir = 'MNISymC_T1/means', atlas_space = 'MNISym', atlas = atlas, maps = maps, rois = atlas)