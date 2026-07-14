import pandas as pd

def week_vols_preprocessing(df):
    df['hemisphere'] = df['regionname'].str[0]

    # subjects with W0
    diff_df = pd.DataFrame()

    for subj in df['subj_id'].unique():
        refT1 = (df.loc[(df['subj_id']==subj), 'RefT1'].iloc[0]).strip()
        if not refT1=='W0':
            #print(subj, "skipped")
            continue
        diff_df = pd.concat([diff_df, df[df['subj_id']==subj]])


    # total wmv per week

    week_vols = diff_df.groupby(['subj_id', 'week', 'Week', 'isPatient', 
                                'hemisphere', 'LesionSide', 'LesionLocation', 'RefT1']
                                ).agg({'nansum': 'sum'}
                                ).reset_index()



    # change in total WM volume relative to the first week per hemisphere (left, right, vermis)

    #for subj in week_vols.loc[week_vols['isPatient']==1, 'subj_id'].unique():
    for subj in week_vols['subj_id'].unique():
        for week in week_vols.loc[week_vols['subj_id']==subj, 'Week'].unique():
            for hem in week_vols.loc[week_vols['subj_id']==subj, 'hemisphere'].unique():
                curr_vol = week_vols.loc[(week_vols['subj_id'] == subj) & (week_vols['Week'] == week) & (week_vols['hemisphere'] == hem), 'nansum'].iloc[0]

                ref_vol = week_vols.loc[(week_vols['subj_id'] == subj) & (week_vols['Week'] == refT1) & (week_vols['hemisphere'] == hem), 'nansum'].iloc[0]
                week_vols.loc[(week_vols['subj_id'] == subj) & (week_vols['Week'] == week) & (week_vols['hemisphere'] == hem), 'vol_diff'] = curr_vol - ref_vol



    # create dummy column: ipsilesional = 0, contralesional = 1, none = 3 (no stroke), vermis = 2

    hem_dict = {
        'L': 'left',
        'R': 'right',
        'V': 'vermis'
    }

    week_vols['hemisphere'] = week_vols['hemisphere'].map(hem_dict) # hem names should match LesionSide names
    # we can use this naming convention in all subsequent cells, so it's fine

    # lesion_namings = {'L': 'left', 'R': 'right', 'l': 'left', 'r': 'right',
    #             'Left': 'left', 'Right': 'right', 'left': 'left', 'right': 'right'}
    week_vols['LesionSide'] = week_vols['LesionSide'].astype(str).str.strip()

    week_vols['side_type'] = 3 # default none

    # for patient rows: set ipsi-, contra-lesional, vermis
    mask_patient = week_vols['isPatient']==1
    mask_hemi_lr = week_vols['hemisphere'].isin(['left', 'right']) # for l, r hem, assign ipsilesional or contralesional

    week_vols.loc[mask_patient & (week_vols['hemisphere'] == week_vols['LesionSide']), 'side_type'] = 0 # ipsi
    week_vols.loc[mask_patient & mask_hemi_lr & (week_vols['hemisphere'] != week_vols['LesionSide']), 'side_type'] = 1 # contra
    week_vols.loc[mask_patient & (week_vols['hemisphere'] == 'vermis'), 'side_type'] = 2 # vermis

    return week_vols
