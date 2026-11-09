import nibabel as nib
import numpy as np
import smarts_cerebellum.globals as gl
from nitools.color import read_lut
import os

def make_cerebellar_roi(atlas, label_num, template, new_label = 1):
    if isinstance(atlas, str):
        atlas = nib.load(atlas)
    # otherwise, assume 'atlas' is nifti image
    if isinstance(template, str):
        template = nib.load(template)

    atlas_arr = atlas.get_fdata().astype(np.int16)
    roi_arr = np.where(np.isin(atlas_arr, label_num), new_label, 0).astype(np.int16)
    
    return nib.Nifti1Image(roi_arr, template.affine)


def lr_cerebellar_atlas(template, lut):
    # cerebellar ROI based on left, right hemishere
    if isinstance(template, str):
        template = nib.load(template)


    left_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[-1]=='L'}
    right_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[-1]=='R'}

    left_cerebellar_roi = make_cerebellar_roi(atlas = cerebellar_roi, label_num = list(left_rois.values()), template = template, new_label = 1)
    right_cerebellar_roi = make_cerebellar_roi(atlas = cerebellar_roi, label_num = list(right_rois.values()), template = template, new_label = 2)

    mega_roi = left_cerebellar_roi.get_fdata() + right_cerebellar_roi.get_fdata()

    return nib.Nifti1Image(mega_roi, template.affine)

def mads_cerebellar_atlas(template, lut):
    # cerebellar ROI based on M, A, D, S parcellation (left, right)
    left_m_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[0]=='M' and label[-1] == 'L'}
    left_a_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[0]=='A' and label[-1] == 'L'}
    left_d_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[0]=='D' and label[-1] == 'L'}
    left_s_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[0]=='S' and label[-1] == 'L'}

    right_m_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[0]=='M' and label[-1] == 'R'}
    right_a_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[0]=='A' and label[-1] == 'R'}
    right_d_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[0]=='D' and label[-1] == 'R'}
    right_s_rois = {label: idx for label, idx in zip(list(lut.values()), list(lut.keys())) if label[0]=='S' and label[-1] == 'R'}

    return ("work in progress")



if __name__ == '__main__':
    template = os.path.join(gl.baseDir, 'ROI', 'tpl-MNI152NLin2009cSymC_T1w.nii')

    # in lut: combine all regions that end in 'L' into one roi
    cerebellar_roi = os.path.join(gl.baseDir, 'ROI', 'Nettekoven_atlases', 'atl-NettekovenSym32_space-MNISym_dseg.nii')
    atlas_lut_name =  'atl-NettekovenSym32.lut'
    lut = os.path.join(gl.baseDir, 'ROI', 'Nettekoven_atlases', atlas_lut_name)

    index, colors, labels = read_lut(lut)
    lut = {int(i): lbl for i, lbl in zip(index, labels)}


    mega_roi = lr_cerebellar_atlas(template = template, lut = lut)
    
    save_path = os.path.join(gl.baseDir, 'ROI', 'Nettekoven_atlases')
    nib.save(mega_roi, os.path.join(save_path, 'atl-NettekovenSym_LeftRight_MNISymC.nii'))
