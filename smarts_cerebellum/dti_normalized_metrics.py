import pandas as pd
import numpy as np
import io
import os
from pathlib import Path
import smarts_cerebellum.globals as gl

def add_normalized_metrics(df):
    # normalize df metrics
    df_wide = df.pivot(index = ['subj_id', 'Week', 'region_bilat'], columns =  'side', values = 'mean')
    df_wide['ratio'] = df_wide['ipsilesional'] / df_wide['contralesional']
    df_wide['log_ratio'] = np.log(df_wide['ratio'])
    df_wide['asymmetry_index'] = (df_wide['contralesional'] - df_wide['ipsilesional']) / (df_wide['contralesional'] + df_wide['ipsilesional'])

    df_wide.columns.name = None
    df_wide = df_wide.reset_index()

    df_long = df_wide.melt(
        id_vars = ['subj_id', 'Week', 'region_bilat', 'ratio', 'log_ratio', 'asymmetry_index'],
        value_vars = ['ipsilesional', 'contralesional'], 
        var_name = 'side', value_name = 'mean'

        )

    keys = ['subj_id', 'Week', 'region_bilat', 'side']
    df_merged = df.merge(df_long[keys + ['ratio', 'log_ratio', 'asymmetry_index']], 
                    on = keys, how = 'left', validate = 'many_to_one')

    return df_merged