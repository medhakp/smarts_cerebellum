#%%
# make summarized dataframe using anatomical atlas Diedrichsen_2009
import pandas as pd
import os
import smarts_cerebellum.globals as gl
from smarts_cerebellum import make_summarized_dataframe_weeks as summ_df_weeks


# MACROS
lme_dir = os.path.join(gl.baseDir, 'lme')

all_weeks = ['W0', 'W4', 'W12', 'W24', 'W52']
groups = ['patients', 'controls']
#groups = ['patients'] # from model - to be concatenated with patients from just
#groups = ['controls']
metrics = ['beta', 'bse']
segments = ['T1', 'GM', 'WM', 'CSF']




# get summary dfs for all: groups - metrics - segments; and concatenate
df_list = []
for gp in groups:
    for m in metrics:
        for s in segments:
            if m == 'beta':
                suffix = 'lme'
                suffix0 = 'lme_beta'
            elif m== 'bse':
                suffix = 'lme_se'
                suffix0 = 'lme_bse'
            df_list.append(summ_df_weeks.make_summ_df(group = gp, metric = m, segment = s, suffix = suffix, suffix0 = suffix0,
                                                      weeks = all_weeks,
                                                      subdir = lme_dir))

summ_df = pd.concat(df_list, axis = 0, ignore_index = True)
summ_df.to_csv(f'{lme_dir}/lme_summarized_df.tsv', sep = '\t', index = False)

# %%

# new df: patients in model, controls with means (of normalized images, not model)


# PATIENTS
df_list = []
for gp in groups:
    for m in metrics:
        for s in segments:
            if m == 'beta':
                suffix = 'lme'
                suffix0 = 'lme_beta'
            elif m== 'bse':
                suffix = 'lme_se'
                suffix0 = 'lme_bse'
            df_list.append(summ_df_weeks.make_summ_df(group = gp, metric = m, segment = s, suffix = suffix, suffix0 = suffix0,
                                                      weeks = all_weeks,
                                                      subdir = lme_dir))


summ_df = pd.concat(df_list, axis = 0, ignore_index = True)
summ_df['isModel'] = 1
summ_df.to_csv(f'{lme_dir}/patients_lme_summarized_df.tsv', sep = '\t', index = False)

# for new df: with patients = model, controls = mean: make each separately, then concat (with col isModel -> bool)

# %%
# excluded_controls = ['CUP_1001', 'UZP_1001', 'UZP_1002', ]
df1 = pd.read_csv(f'{lme_dir}/patients_lme_summarized_df.tsv', sep = '\t')
df2 = pd.read_csv(f'{lme_dir}/controls_mean_summarized_df.tsv', sep = '\t')

dfs = pd.concat([df1, df2], axis = 0, ignore_index = True)
dfs.to_csv(f'{lme_dir}/pc_lme_summarized_df.tsv', sep = '\t', index = False)
# %%
