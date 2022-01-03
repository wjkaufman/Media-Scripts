'''
author: Will Kaufman
created: 2021-11-03
modified: 2021-11-19

Call this script by running:
`python rename_by_filename.py /path/to/pictures`

This script should walk through the given path,
recording existing metadata for pictures, and guessing
the correct metadata based on the filename

Commands to do after:

tar -czf _metadata.tar.gz **/*_metadata.txt
rm **/*_metadata.txt


TODO:
- It seems like files with YYYY-MM-DD-HHMMSS format are updated regardless.
    Don't do that if the original metadata looks good!!!
- Check existing metadata against filename, if it's close then leave as-is
- Add png support (this should be easy using exiftool)


Resources:

https://stackoverflow.com/questions/4760215/
running-shell-command-and-capturing-the-output
'''

import os
import sys
import re
import pandas as pd
import subprocess
from datetime import datetime
# from traceback import print_tb


def guess_date(filename):
    '''
    guess_date('2021-03-19-195432.jpg') should work
    
    guess_date('2021-14-19-195432.jpg')
    guess_date('2021-04-19-199132.jpg')
    
    '''
    # first try to see if there is YMDHMS data
    m = re.match(r'([0-9]{4})-([0-9]{2})-([0-9]{2})-([0-9]{6})(.*)', filename)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        hour = int(m.group(4)[:2])
        minute = int(m.group(4)[2:4])
        second = int(m.group(4)[4:6])
        assert 1700 < year < 2025
        assert 1 <= month <= 12
        assert 1 <= day <= 31
        assert 0 <= hour <= 23
        assert 0 <= minute <= 59
        assert 0 <= second <= 59
        return (year, month, day,
                hour, minute, second)
    
    # then try to see if there is YMD order data
    m = re.match(
        r'([0-9]{4})-([0-9]{2})-([0-9]{2})([^0-9]+?)([0-9]+)(.*?)', filename)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        order = int(m.group(5))
        if day == 0:
            day = 1
        assert 1700 < year < 2025
        assert 1 <= month <= 12
        assert 1 <= day <= 31
        return (year, month, day, order)
    
    # then try to see if there is YMD data
    m = re.match(
        r'([0-9]{4})-([0-9]{2})-([0-9]{2})([^0-9]+?)(.*?)', filename)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        order = 0
        if day == 0:
            day = 1
        assert 1700 < year < 2025
        assert 1 <= month <= 12
        assert 1 <= day <= 31
        return (year, month, day, order)
    
    # then try to see if there is year, month, order data
    m = re.match(r'([0-9]{4})-([0-9]{2})([^0-9]+?)([0-9]+)(.*)', filename)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        order = int(m.group(4))
        if month == 0:
            # manually change month
            month = 1
        assert 1700 < year < 2025
        assert 1 <= month <= 12
        return (year, month, order)
    
    # then try to see if there is year, month data
    m = re.match(r'([0-9]{4})-([0-9]{2})([^0-9]+?)(.*)', filename)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        order = 0
        if month == 0:
            # manually change month
            month = 1
        assert 1700 < year < 2025
        assert 1 <= month <= 12
        return (year, month, order)
    
    # then try to see if there is year, order data
    m = re.match(r'([0-9]{4}) ([0-9]+)(.*)', filename)
    if m:
        year = int(m.group(1))
        order = int(m.group(2))
        assert 1700 < year < 2025
        return (year, order)
    
    # finally try to see if there is year data
    m = re.match(r'([0-9]{4})(.*)', filename)
    if m:
        year = int(m.group(1))
        order = 0  # hard coding because there's no order data
        assert 1700 < year < 2025
        return (year, order)
    
    return ()


def get_metadata(filepath):
    '''
    Get metadata from given filepath
    '''
    # get filesize
    fsize = os.path.getsize(filepath)
    # get current metadata
    result = subprocess.run(['exiftool', filepath], stdout=subprocess.PIPE)
    metadata = result.stdout.decode('utf-8')
    metadata = f'metadata for {filepath}\nfile size = {fsize}\n' + metadata
    return metadata


def save_metadata(filepath, old_metadata):
    '''
    Save metadata to a separate file in case it's useful later
    '''
    with open(filepath + '_metadata.txt', 'w') as f:
        f.write(old_metadata)
    print(f'saved metadata for {filepath}')


def get_date_from_metadata(metadata):
    '''
    Try a few different regex matches on the metadata string
    and return the date if possible. Returns None if
    no date match happens.
    '''
    
    m = re.search(r'^Date/Time Original\W+:\W+'
                  + r'([0-9]{4}):([0-9]{2}):([0-9]{2}) .+',
                  metadata,
                  flags=re.MULTILINE)
    
    if not m:  # if there wasn't a match
        m = re.search(r'^Create Date\W+:\W+'
                      + r'([0-9]{4}):([0-9]{2}):([0-9]{2}) .+',
                      metadata,
                      flags=re.MULTILINE)
    
    # 2021-11-21: If date/time original isn't there, I believe (after a
    # brief test) that file modification date/time is then used as the
    # metadata.
    if not m:  # if there wasn't a match
        m = re.search(r'^File Modification Date/Time\W+:\W+'
                      + r'([0-9]{4}):([0-9]{2}):([0-9]{2}) .+',
                      metadata,
                      flags=re.MULTILINE)
    
    if m:
        return (int(m.group(1)),
                int(m.group(2)),
                int(m.group(3)))
    
    return


def change_metadata(filepath, new_date):
    '''
    Actually change the metadata in the picture
    
    change_metadata('1998-01 002.JPG', (1998, 1))
    '''
    # year and order data only
    if len(new_date) == 2:
        year, order = new_date
        month = 1
        day = 1
    elif len(new_date) == 3:
        year, month, order = new_date
        day = 1
    elif len(new_date) == 4:
        year, month, day, order = new_date
    elif len(new_date) == 6:
        year, month, day, hour, minute, second = new_date
        order = None
    else:
        raise NotImplementedError('Whoops, have not done this yet!!!')
    
    # get time from order
    if type(order) is int:
        hour = 0
        minute = int(order / 60)
        second = order % 60
    
    subprocess.run(  # result =
        ['exiftool',
         '-overwrite_original',
         # or can set all tags with time:all instead of datetimeoriginal
         f'-datetimeoriginal={year:04.0f}:{month:02.0f}:{day:02.0f}'
         + f'{hour:02.0f}:{minute:02.0f}:{second:02.0f}',  # -06:00
         filepath],
        stdout=subprocess.PIPE)
    # print(result.stdout.decode('utf-8'))
    print(f'changed metadata for {filepath} (now {(year, month, day)})')
    
    pass


if __name__ == '__main__':
    path = sys.argv[1]
    # change to target directory
    os.chdir(path)

    print(f'Walking through {path}')
    
    updated_filepaths = []
    updated_old = []
    updated_new = []

    failed_dirpaths = []
    failed_files = []
    
    ignored_filepaths = []

    for dirpath, _, files in os.walk('.'):
        for f in files:
            filepath = os.path.join(dirpath, f)
            # check if f is a jpg
            m = re.match(
                # jpg|JPG|jpeg|JPEG|png|PNG|mp4|MP4|mov|MOV|m4v|M4V
                r'.*\.(jpg|JPG|jpeg|JPEG|png|PNG|mp4|MP4|m4v|M4V)$', f)
            if m is None:
                # failed_dirpaths.append(dirpath)
                # failed_files.append(f)
                ignored_filepaths.append(filepath)
                continue
            # print(f'looking at {filepath} next')
            try:
                date = guess_date(f)
                old_metadata = get_metadata(filepath)
                metadata_date = get_date_from_metadata(old_metadata)
                # compare metadata date and filename date, if they match
                # then don't rename
                if ((len(date) == 2
                     and metadata_date[0] == date[0])
                    or (len(date) == 3
                        and metadata_date[0] == date[0]
                        and metadata_date[1] == date[1])
                    or (len(date) >= 4
                        and metadata_date[0] == date[0]
                        and metadata_date[1] == date[1]
                        and metadata_date[2] == date[2])):
                    # print('Filename date and metadata date match!')
                    pass
                else:
                    save_metadata(filepath, old_metadata)
                    # the filename and metadata don't match, so renaming
                    # based on filename
                    # print(f'Filename date ({date}) does not match metadata '
                    #       + f'({metadata_date})')
                    change_metadata(filepath, date)
                    
                    updated_filepaths.append(filepath)
                    updated_old.append(str(metadata_date))
                    updated_new.append(str(date))
            except Exception as e:
                print(f'failed on {filepath}:')
                print(e)
                # print_tb()
                failed_dirpaths.append(dirpath)
                failed_files.append(f)
    
    now_str = datetime.now().strftime('%Y%m%d%H%M%S')
    
    updated = pd.DataFrame({
        'filepath': updated_filepaths,
        'old_metadata': updated_old,
        'new_metadata': updated_new
    })
    updated.to_csv(f'{now_str}_updated_metadata.csv', index=False)
    
    failures = pd.DataFrame({
        'dirpath': failed_dirpaths,
        'filename': failed_files
    })
    failures.to_csv(f'{now_str}_failures_update.csv', index=False)
    
    ignores = pd.DataFrame({
        'filepath': ignored_filepaths
    })
    ignores.to_csv(f'{now_str}_ignored_update.csv', index=False)

    print('Done!')
