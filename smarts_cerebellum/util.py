import pandas as pd
import numpy as np


def tract_df(df, tract = 'CST'):
    # cut dataframe: patients left, right; controls bilateral tract (e.g. CST)
    patients = df[df.isPatient == 1]
    controls = df[df.isPatient == 0]

    r_patients = np.array(df[(df.isPatient == 1) & (df.regionname == f'right_{tract}')]['mean'])
    l_patients = np.array(df[(df.isPatient == 1) & (df.regionname == f'left_{tract}')]['mean'])
    
    controls_bilat = controls.groupby('subj_id').agg({'mean': 'mean'}).reset_index()
    controls_bilat['regionname'] = f'bilat_{tract}'
    controls_bilat['isPatient'] = 0
    
    b_controls = np.array(controls_bilat['mean'])
    patients_lr = patients[patients.regionname.isin([f'left_{tract}', f'right_{tract}'])]
    tract_df = pd.concat([patients_lr, controls_bilat], ignore_index=True)

    return r_patients, l_patients, b_controls, tract_df
