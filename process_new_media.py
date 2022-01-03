'''

Rename all media files in a given directory, and move the
file depending on the status of the file's metadata.

Run as `python process_new_media.py /path/to/media`
'''

import os
import sys
from exiftool import (
    ExifTool, is_jpg, is_png, is_mov, is_mp4, is_m4v,
    get_jpg_date, get_png_date, get_mov_date, get_mp4_date,
    get_m4v_date
)


if __name__ == '__main__':
    
    path = sys.argv[1]
    
    os.chdir(path)
    
    with ExifTool() as e:
        # TODO
        # TODO
        # TODO
        # TODO
        # TODO
        for f in os.listdir():
            try:
                metadata = e.read_metadata(f)
                if is_jpg(f):
                    date = get_jpg_date(metadata)
                elif is_png(f):
                    date = get_png_date(metadata)
                elif is_mov(f):
                    date = get_mov_date(metadata)
                elif is_mp4(f):
                    date = get_mp4_date(metadata)
                elif is_m4v(f):
                    date = get_m4v_date(metadata)
                else:
                    raise ValueError(f'{f} is unsupported filetype')
                # TODO continue here...
                new_f = rename(f, date)
                records.append({f: new_f})
                f = new_f
                if not has_good_date(metadata):
                    move(f, 'to_check/')
                else:
                    move(f, 'done/')
            except Exception as exception:
                print(f'failed on {f}')
                print(exception)
    pass
