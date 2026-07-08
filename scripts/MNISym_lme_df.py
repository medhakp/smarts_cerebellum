#%%
# make summarized dataframe using anatomical atlas Diedrichsen_2009
import SUITPy as suit
import os
import pandas as pd
import smarts_cerebellum.globals as gl


# MACROS
lme_dir = os.path.join(gl.baseDir, 'lme')

all_weeks = ['W0', 'W4', 'W12', 'W24', 'W52']
groups = ['patients', 'controls']
metrics = ['beta', 'bse']
segments = ['T1', 'GM', 'WM', 'CSF']


# finds one file per week
def _image_paths(group, prefix, suffix, suffix0, segment, weeks = all_weeks):
    images = []
    for week in weeks:
        if not week == 'W0':
            file = f'{lme_dir}/{segment}/{group}_{prefix}_{week}_{suffix}.nii.gz'
        else: # week0 files are named differently...like with beta rather than lme
            file = f'{lme_dir}/{segment}/{group}_{prefix}_{week}_{suffix0}.nii.gz'
        images.append(file)
    return images



# dataframe will just be: image, roi, (other atlas_summary cols), isPatient (add this one), week (add)

def _summary_df(images, # image for each: group-param-segment
                group, param, segment,
                the_atlas = 'Diedrichsen_2009', maps = 'atl_Anatom', space = 'MNISym'):
     suit.fetch_atlas(the_atlas)

     df = suit.summarize_data(images = images, atlas = the_atlas, maps = maps, space = space,
                              stats = ['mean', 'median', 'nansum']
                              )
     
     df['group'] = group
     df['param'] = param # betas or bse?
     df['segment'] = segment # T1, GM, WM, CSF

     # find the week token from image_name (for each image)
     week_tokens = ['W0', 'W4', 'W12', 'W24', 'W52']

     for img in images:
          # use next to go through list (iteration); sort in ascending order
          week_val = next((w for w in sorted(week_tokens) if w in img), None) # None if week_token not found

          # img is a path; just want the file name
          img_file = os.path.basename(img)

          # in image row, add its week
          df.loc[df.image_name == img_file, 'Week'] = week_val
          #df[df.image_name == img_file]['Week'] = week_val

     return df


def make_summ_df(group, metric, segment):
    prefix = f'MNISymC_{segment}'
    suffix = 'lme' if metric == 'beta' else 'lme_se'
    suffix0 = 'lme_beta' if metric == 'beta' else 'lme_bse'

    # find all image paths
    images = _image_paths(group = group, prefix = prefix, suffix = suffix, suffix0 = suffix0, segment = segment)
    
    # make summary df
    df = _summary_df(images = images, group = group, param = metric, segment = segment)

    return df

# get summary dfs for all: groups - metrics - segments; and concatenate
df_list = []
for gp in groups:
    for m in metrics:
        for s in segments:
            df_list.append(make_summ_df(group = gp, metric = m, segment = s))

summ_df = pd.concat(df_list, axis = 0, ignore_index = True)
summ_df.to_csv(f'{lme_dir}/lme_summarized_df.tsv', sep = '\t', index = False)

# %%
