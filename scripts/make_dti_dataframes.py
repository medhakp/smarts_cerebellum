import pandas as pd
import io
import os
from pathlib import Path
import smarts_cerebellum.globals as gl


def _subj_week_loop(df):
    for i in range(0, df.shape[0]):
        p_id = df['ID'].iloc[i]
        week = (df['Week'].iloc[i]).strip() # sometimes have extra white spaces
        p_centre = (str(df['Centre'].iloc[i])).strip()
        subj_id = f'{p_centre.strip()}_{p_id}'

        # return each subj_id, week one at a time
        yield subj_id, week


def subj_dti_df(subj_id, week):
    # Claude helped
    path = os.path.join(gl.baseDir, 'DTI', subj_id, week)
    file = 'JHU_MNI_SS_WMPM_TypeII_ver2.1_dti.txt'
    file_path = os.path.join(path, file)

    if not Path(file_path).exists():
        return None

    cols = ['Image', 'Object', 'Pixels', 'Min', 'Max', 'Mean', 'Std'] # columns to use

    # data lines start with "G:"; others are headers
    with open(file_path, "r", encoding = "utf-8") as f:
        data_lines = [line for line in f if line.startswith("G:")]

    df = pd.read_csv(io.StringIO("".join(data_lines)), sep = '\t', names = cols, usecols = range(7))
    df['metric'] = df['Image'].str.extract(r'\\([^\\]+)\.dat$') # get metric (from image name, using re method)
    df['subj_id'] = subj_id
    df['week'] = week
    df['week_num'] = df['week'].str.extract(r'(\d+)') # get numeric values

    return df


   
if __name__ == '__main__':
    p_dti = pd.read_excel(os.path.join(gl.baseDir, 'DTI', 'patient_list.xlsx'), usecols = range(5)) # only need the first 5 cols

    dfs = []

    for subj, week in _subj_week_loop(p_dti):
        df = subj_dti_df(subj, week)
        if df is not None:
            dfs.append(df)

        all_df = pd.concat(dfs, ignore_index = True)

    all_df.to_csv(os.path.join(gl.baseDir, 'DTI', 'JHU_MNI_DTI.tsv'), sep = '\t', index = False)
