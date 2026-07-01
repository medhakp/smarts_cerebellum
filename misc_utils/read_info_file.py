"""
Literally just reads the participants information file; to be used in other modules.

Maybe not needed. We'll see.
"""

# Importd
import pandas as pd
from pathlib import Path
import os

# directories
base_dir = '/cifs/diedrichsen/data/smarts_cerebellum'
anat_dir = '/cifs/diedrichsen/data/smarts_cerebellum/anatomicals'
p_df = pd.read_csv(f'{base_dir}/participants_anat.tsv', sep = '\t')