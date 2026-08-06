import pandas as pd
import numpy as np
import re
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import nibabel as nib
import nitools as nt
import SUITPy
import smarts_cerebellum.globals as gl


def wb_command():
    """
    @Authors: Marco,

    Finds the wb_command executable. Looks on the PATH first, then at $WB_COMMAND,
    then at gl.wbDir - jupyter kernels don't source .bashrc, so the PATH set there
    is usually not visible from a notebook.

    Returns:
        exe (str): path to wb_command
    """
    exe = shutil.which('wb_command')
    if exe is not None:
        return exe

    for cand in [os.environ.get('WB_COMMAND'), os.path.join(gl.wbDir, 'wb_command')]:
        if cand is not None and os.access(cand, os.X_OK):
            return cand

    raise FileNotFoundError(
        'wb_command not found. Put it on the PATH, set $WB_COMMAND to the '
        f'executable, or point gl.wbDir at its folder (currently {gl.wbDir})')


def suit_midthickness(space = 'MNISymC'):
    """
    @Authors: Marco,

    Builds the SUIT midthickness surface (mean of WHITE and PIAL) to smooth on.
    Geodesic distances on the flatmap are distorted, so smoothing should happen
    on the 3d surface, not on FLAT.surf.gii.

    Args:
        space: 'MNISymC', 'SUIT', 'SPM' or 'FSL'

    Returns:
        surf (nb.GiftiImage): midthickness surface
    """
    surf_dir = os.path.join(os.path.dirname(SUITPy.__file__), 'surfaces')

    surf = nib.load(os.path.join(surf_dir, f'WHITE_{space}.surf.gii'))
    pial = nib.load(os.path.join(surf_dir, f'PIAL_{space}.surf.gii'))

    # keep the white surface as the container (metadata, coordinate system,
    # int32 triangles) and only swap in the averaged coordinates
    coords = surf.agg_data('NIFTI_INTENT_POINTSET')
    coords[:] = (coords + pial.agg_data('NIFTI_INTENT_POINTSET')) / 2

    return surf


def smooth_gifti(gifti,
                 surf = None,
                 space = 'MNISymC',
                 sigma = 2.0,
                 fwhm = False,
                 fix_zeros = True
                 ):
    """
    @Authors: Marco,

    Smooths a functional gifti along the cerebellar surface with
    wb_command -metric-smoothing.

    NaNs are set to 0 before smoothing (so they don't spread into their
    neighbours) and put back afterwards. The output also has NaNs at the 101
    vertices of the SUIT mesh that no triangle references: they have no
    neighbourhood to smooth over, and no triangle renders them either.

    Args:
        gifti: GiftiImage or filename (num_vert x num_col)
        surf: Surface GiftiImage or filename to smooth on. Defaults to the SUIT
            midthickness for `space`.
        space: Space of the default surface ('MNISymC', 'SUIT', 'SPM', 'FSL')
        sigma: Kernel size in mm (sigma, or FWHM if fwhm is True)
        fwhm: If True, `sigma` is interpreted as FWHM
        fix_zeros: Pass -fix-zeros, so zeros are treated as missing data rather
            than pulling their neighbours down

    Returns:
        gifti_out (nb.GiftiImage): smoothed functional gifti
    """
    if isinstance(gifti, (str, Path)):
        gifti = nib.load(gifti)
    if surf is None:
        surf = suit_midthickness(space = space)
    elif isinstance(surf, (str, Path)):
        surf = nib.load(surf)

    data = np.c_[gifti.agg_data()]
    if data.ndim == 1:
        data = data.reshape(-1, 1)

    nan_mask = np.isnan(data)
    column_names = nt.get_gifti_column_names(gifti)

    with tempfile.TemporaryDirectory() as tmp_dir:
        surf_file = os.path.join(tmp_dir, 'surf.surf.gii')
        in_file = os.path.join(tmp_dir, 'in.func.gii')
        out_file = os.path.join(tmp_dir, 'out.func.gii')

        nib.save(surf, surf_file)
        nib.save(nt.make_func_gifti(np.nan_to_num(data),
                                    anatomical_struct = 'Cerebellum',
                                    column_names = column_names), in_file)

        cmd = [wb_command(), '-metric-smoothing',
               surf_file, in_file, str(sigma), out_file]
        if fwhm:
            cmd.append('-fwhm')
        if fix_zeros:
            cmd.append('-fix-zeros')

        # capture the output, so wb_command's error shows up in the notebook
        # rather than only in the terminal the kernel was started from
        out = subprocess.run(cmd, capture_output = True, text = True)
        if out.returncode != 0:
            raise RuntimeError(f'{" ".join(cmd)}\n{out.stdout}{out.stderr}')

        smoothed = np.c_[nib.load(out_file).agg_data()]

    if smoothed.ndim == 1:
        smoothed = smoothed.reshape(-1, 1)
    smoothed[nan_mask] = np.nan

    return nt.make_func_gifti(smoothed,
                              anatomical_struct = nt.get_gifti_anatomical_struct(gifti),
                              column_names = column_names)


def gifti_to_cifti(gifti,
                   structure = 'cerebellum',
                   column_names = None,
                   mask_nan = True
                   ):
    """
    @Authors: Marco,

    Makes a dscalar Cifti2Image from a functional gifti on a single surface
    (e.g. the SUIT cerebellar flatmap).

    Args:
        gifti: GiftiImage or filename (num_vert x num_col)
        structure: Cifti brain structure name (e.g. 'cerebellum', 'cortex_left')
        column_names: List of names, one per column. Defaults to the gifti's
            column names.
        mask_nan: If True, vertices that are NaN in every column are left out of
            the brain model (rather than stored as NaN)

    Returns:
        cifti_img (nb.Cifti2Image): dscalar image
    """
    if isinstance(gifti, (str, Path)):
        gifti = nib.load(gifti)

    data = np.c_[gifti.agg_data()]
    if data.ndim == 1:
        data = data.reshape(-1, 1)

    n_vert, n_cols = data.shape

    if column_names is None:
        column_names = nt.get_gifti_column_names(gifti)
    if len(column_names) != n_cols:
        raise ValueError(f'{len(column_names)} column names for {n_cols} columns')

    if mask_nan:
        vertices = np.where(np.any(np.isfinite(data), axis = 1))[0]
    else:
        vertices = np.arange(n_vert)

    bm_axis = nib.cifti2.BrainModelAxis.from_surface(vertices, n_vert, name = structure)
    scalar_axis = nib.cifti2.ScalarAxis(column_names)

    header = nib.Cifti2Header.from_axes((scalar_axis, bm_axis))

    return nib.Cifti2Image(dataobj = data[vertices].T, header = header)


def preprocess_tract_df(df, tract = 'CST'):
    # cut dataframe: patients left, right; controls bilateral tract (e.g. CST)
    patients = df[df.isPatient == 1]
    controls = df[df.isPatient == 0].copy()

    r_patients = np.array(df[(df.isPatient == 1) & (df.regionname == f'right_{tract}')]['mean'])
    l_patients = np.array(df[(df.isPatient == 1) & (df.regionname == f'left_{tract}')]['mean'])
    

    controls['region_bilat'] = controls.regionname.str[0]
    controls_bilat = controls.groupby(['subj_id', 'region_bilat']).agg({'mean': 'mean'}).reset_index()
    controls_bilat['regionname'] = f'bilat_{tract}'
    controls_bilat['isPatient'] = 0
    
    b_controls = np.array(controls_bilat['mean'])
    patients_lr = patients[patients.regionname.isin([f'left_{tract}', f'right_{tract}'])]
    tract_df = pd.concat([patients_lr, controls_bilat], ignore_index=True)

    return r_patients, l_patients, b_controls, tract_df