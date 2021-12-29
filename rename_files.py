'''
author: Will Kaufman
created: 2021-12-20

Call this script by running:
`python rename_files.py /path/to/directory`

This script should walk through the given path,
renaming all files that match a given criterion.

Will save a csv file of all renamed files

'''

import os
import sys
import re
import pandas as pd
from datetime import datetime

path = sys.argv[1]

if __name__ == '__main__':
    # change to target directory
    os.chdir(path)

    print(f'Walking through {path}')
    
    old_filepaths = []
    new_filepaths = []

    failed_dirpaths = []
    failed_files = []

    for dirpath, _, files in os.walk('.'):
        for f in files:
            # if f matches pattern to rename
            m = re.match(
                r'^(\d{4}-\d{2}-\d{2})_(.*)$', f)
            if m is None:
                # print('no match')
                continue
            filepath = os.path.join(dirpath, f)
            try:
                f_renamed = f'{m.group(1)}-{m.group(2)}'  # rename it
                filepath_renamed = os.path.join(dirpath, f_renamed)
                print(f'{filepath} -> {filepath_renamed}')
                os.rename(filepath, filepath_renamed)
                old_filepaths.append(filepath)
                new_filepaths.append(filepath_renamed)
            except Exception as e:
                print(f'failed on {filepath}:')
                print(e)
                failed_dirpaths.append(dirpath)
                failed_files.append(f)

    now = datetime.now()
    now_str = now.strftime('%Y%m%d%H%M%S')
    failures = pd.DataFrame(
        {'dirpath': failed_dirpaths, 'filename': failed_files})
    failures.to_csv(f'_failures{now_str}.csv', index=False)
    renamed = pd.DataFrame(
        {
            'old_filepath': old_filepaths,
            'new_filepath': new_filepaths
        }
    )
    renamed.to_csv(f'_renamed{now_str}.csv', index=False)

    print('Done!')
