baseDir = '/cifs/diedrichsen/data/smarts_cerebellum/'

# jupyter kernels don't source .bashrc, so wb_command is often not on the PATH
wbDir = '/srv/software/connectome_workbench/2.0.1/bin_linux64'

bad = [] #['CU_2663', 'CUP_1002', 'JHP_1004']

Hem = ['l', 'r']

side = ['Contralesional', 'Ipsilesional', ]

weeks = [0, 4, 12, 24, 52]

rois = {'Nettekoven2024': ['M1', 'M2', 'M3', 'M4',
                           'A1', 'A2', 'A3', 
                           'D1', 'D2', 'D3', 'D4', 
                           'S1', 'S2', 'S3', 'S4', 'S5']}

# consistent font sizes
import matplotlib.pyplot as plt
figure_settings = {
    'axes.titlesize': 11,
    'axes.labelsize': 9,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 9,
    'figure.titlesize': 12
}
plt.rcParams.update(figure_settings)