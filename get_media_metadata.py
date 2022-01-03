'''

Rename all media files in a given directory, and move the
file depending on the status of the file's metadata.

Run as `python process_new_media.py /path/to/media`
'''

import os
import sys
from exiftool import (
    ExifTool, is_jpg, is_png, is_mov, is_mp4, is_m4v,
    # get_jpg_date, get_png_date, get_mov_date, get_mp4_date,
    # get_m4v_date
)


def add_example_tags(new_tags, tag_set, new_file, example_list):
    if new_tags not in tag_set:
        tag_set.add(new_tags)
        example_list.append(new_file)


if __name__ == '__main__':
    
    path = sys.argv[1]
    original_path = os.getcwd()
    
    os.chdir(path)
    
    examples = []
    jpg_metadata_tags = set()  # save tags, unique, etc.
    png_metadata_tags = set()
    mov_metadata_tags = set()
    mp4_metadata_tags = set()
    m4v_metadata_tags = set()
    with ExifTool() as e:
        for dirpath, dirnames, filenames in os.walk('.'):
            for f in filenames:
                try:
                    metadata = e.read_time_metadata(f)[0]
                    keys = tuple(metadata.keys())
                    if is_jpg(f):
                        add_example_tags(keys, jpg_metadata_tags, f, examples)
                    elif is_png(f):
                        add_example_tags(keys, png_metadata_tags, f, examples)
                    elif is_mov(f):
                        add_example_tags(keys, mov_metadata_tags, f, examples)
                    elif is_mp4(f):
                        add_example_tags(keys, mp4_metadata_tags, f, examples)
                    elif is_m4v(f):
                        add_example_tags(keys, m4v_metadata_tags, f, examples)
                except Exception as exception:
                    print(f'failed on {f}')
                    print(exception)
    os.chdir(original_path)
    with open('_tags.txt', 'a') as f:
        f.write(str(jpg_metadata_tags) + '\n')
        f.write(str(png_metadata_tags) + '\n')
        f.write(str(mov_metadata_tags) + '\n')
        f.write(str(mp4_metadata_tags) + '\n')
        f.write(str(m4v_metadata_tags) + '\n')
        f.write('\n' * 5 + str(examples))
