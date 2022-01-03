from datetime import datetime
import subprocess
import os
import json


class ExifTool(object):

    sentinel = "{ready}\n"

    def __init__(self, executable="/usr/local/bin/exiftool"):
        self.executable = executable

    def __enter__(self):
        self.process = subprocess.Popen(
            [
                self.executable,
                "-stay_open", "True",  "-@", "-"
            ],
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.process.stdin.write("-stay_open\nFalse\n")
        self.process.stdin.flush()

    def execute(self, *args):
        args = args + ("-execute\n",)
        self.process.stdin.write(str.join("\n", args))
        self.process.stdin.flush()
        output = ""
        fd = self.process.stdout.fileno()
        while not output.endswith(self.sentinel):
            output += os.read(fd, 4096).decode('utf-8')
        return output[:-len(self.sentinel)]

    def read_metadata(self, *filenames):
        return json.loads(self.execute(
            '-G', '-j', '-n',
            *filenames
        ))
    
    def read_time_metadata(self, *filenames):
        return json.loads(self.execute(
            '-G', '-j', '-n', '-time:all',
            *filenames
        ))
    
    def write_metadata(self, filename, tags):
        '''
        Args:
            tags (dict): A dictionary where the keys are metadata tags
                and the values are the values.
        '''
        args = [f'-{k}={tags[k]}' for k in tags]
        self.execute(*args, filename)


def is_jpg(f):
    _, ext = os.path.splitext(f)
    if ext.lower() in ['.jpg', '.jpeg']:
        return True
    else:
        return False


def is_png(f):
    _, ext = os.path.splitext(f)
    if ext.lower() in ['.png']:
        return True
    else:
        return False


def is_mov(f):
    _, ext = os.path.splitext(f)
    if ext.lower() in ['.mov']:
        return True
    else:
        return False


def is_mp4(f):
    _, ext = os.path.splitext(f)
    if ext.lower() in ['.mp4']:
        return True
    else:
        return False


def is_m4v(f):
    _, ext = os.path.splitext(f)
    if ext.lower() in ['.m4v']:
        return True
    else:
        return False


def get_date(date_str):
    return datetime.strptime(
        date_str.replace(':', ''),
        '%Y%m%d %H%M%S%z'
    )


def get_jpg_date(metadata):
    if 'EXIF:DateTimeOriginal' in metadata.keys():
        date_str = metadata['EXIF:DateTimeOriginal']
    elif 'EXIF:CreateDate' in metadata.keys():
        date_str = metadata['EXIF:CreateDate']
    else:
        date_str = metadata['File:FileModifyDate']
    return get_date(date_str)


def get_png_date(metadata):
    if 'EXIF:DateTimeOriginal' in metadata.keys():
        date_str = metadata['EXIF:DateTimeOriginal']
    else:
        date_str = metadata['File:FileModifyDate']
    return get_date(date_str)


def get_mov_date(metadata):
    if 'QuickTime:CreationDate' in metadata.keys():
        date_str = metadata['QuickTime:CreationDate']
    else:
        date_str = metadata['File:FileModifyDate']
    return get_date(date_str)


def get_mp4_date(metadata):
    if 'QuickTime:CreateDate' in metadata.keys():
        date_str = metadata['QuickTime:CreateDate']
    else:
        date_str = metadata['File:FileModifyDate']
    return get_date(date_str)


def get_m4v_date(metadata):
    if 'QuickTime:ContentCreateDate' in metadata.keys():
        date_str = metadata['QuickTime:ContentCreateDate']
    else:
        date_str = metadata['File:FileModifyDate']
    return get_date(date_str)
