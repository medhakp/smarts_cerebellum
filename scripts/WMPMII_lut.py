import pandas as pd
import os
import smarts_cerebellum.globals as gl

dti = pd.read_csv(os.path.join(gl.baseDir, 'DTI', 'WMPMII_DTI_flip.tsv'), sep = '\t')
rois_df = pd.DataFrame({'label': range(len(dti.regionname.unique())), 'regionname': dti.regionname.unique()})
rois_df.to_csv(os.path.join(gl.baseDir, 'ROI', 'WMPMII_labels.tsv'), sep = '\t', index = False)