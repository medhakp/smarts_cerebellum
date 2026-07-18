
# make summarized dataframe using anatomical atlas Diedrichsen_2009
import SUITPy as suit
import os
import smarts_cerebellum.globals as gl


# finds one file per week
# ref_file instead; specific ref_file for week0 if required? or rename week0 file
def _image_paths(group, prefix, suffix, segment, weeks, subdir, suffix0 = None):
    images = []
    for week in weeks:
        if week != 'W0' or suffix0 == 'None': # if week0 has different name
            file = f'{subdir}/{segment}/{group}_{prefix}_{week}_{suffix}.nii.gz'
            print('same week0')
        else: # week0 files are named differently...like with beta rather than lme
            file = f'{subdir}/{segment}/{group}_{prefix}_{week}_{suffix0}.nii.gz'
            print('diff W0')
        images.append(file)
    return images



# dataframe will just be: image, roi, (other atlas_summary cols), isPatient (add this one), week (add)

def _summary_df(images, # image for each: group-param-segment
                group, param, segment,
                the_atlas = 'Diedrichsen_2009', maps = 'atl-Anatom', space = 'MNISym'):
     suit.fetch_atlas(the_atlas)

     df = suit.summarize_data(images = images, atlas = the_atlas, maps = maps, space = space,
                              stats = ['mean', 'median', 'nansum']
                              )
     
     df['group'] = group
     df['param'] = param # betas or bse? etc.
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

     return df


def make_summ_df(group, metric, segment, weeks, subdir, suffix, suffix0 = 'None', space = 'MNISymC'):
    prefix = f'{space}_{segment}'


    # find all image paths
    images = _image_paths(group = group, prefix = prefix, suffix = suffix, suffix0 = suffix0, segment = segment,
                          weeks = weeks, subdir = subdir)
    
    # make summary df
    df = _summary_df(images = images, group = group, param = metric, segment = segment)

    return df

