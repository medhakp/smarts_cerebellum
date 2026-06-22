import re
from pathlib import Path

"""
Searches for files in all possible weeks that match the path structure of a reference file.

e.g. if you want to find all anatomicals for a given subject over all weeks.
"""

def week_path_search(reference_file, weeks = [0, 4, 12, 24, 52]):
    """
    Inputs:
        reference_file (str): path to a file whose path will be used as reference.
            That is, this file's path should have the structure that all other files from that week should have.
        weeks: weeks in filepath
    
    Outputs:
        week_paths (list[str]): paths to all files (including reference) that exist for weeks
        week_available (list[str]): weeks whose files exist
    """

    ref_path = str(reference_file)

    # find all places in path with the week
    match = re.search(r'W(\d+)', ref_path)
    if not match:
        print(f'could not find week token in reference path for {ref_path}')
        return None
    
    ref_week_token = match.group(1) # return entire text that ws matched.

    weeks_paths = []
    weeks_available = []

    for week in weeks:
        # search for every week's file

        # replace the week token(s) in reference image path with other tokens for new week path
        #week_path = ref_path.replace(ref_week_token, f'W{week}')

        week_path = re.sub(rf'W{ref_week_token}(?!\d)', f'W{week}', ref_path)

        if not Path(week_path).exists():
            print(f'skipping W{week}')
            continue

        weeks_paths.append(week_path)
        weeks_available.append(week) # add weeks as integers

    return weeks_paths, weeks_available