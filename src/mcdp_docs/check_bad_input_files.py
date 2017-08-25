from mcdp_utils_misc.locate_files_imp import locate_files
from collections import defaultdict
import os
from compmake.utils.friendly_path_imp import friendly_path

def collect_by_extension(d):
    fs = locate_files(d, '*')
    ext2filename = defaultdict(list)
    for filename in fs:
        basename = os.path.basename(filename)
        _, ext = os.path.splitext(basename)
        ext2filename[ext].append(filename)
    return ext2filename

from mcdp import logger

def check_bad_input_file_presence(d):

    ext2filenames = collect_by_extension(d)
    s = '## Filename extensions statistics'
    s += "\nFound in %s:" % friendly_path(d)
    for ext in sorted(ext2filenames, key=lambda k: -len(ext2filenames[k])):
        x = ext if  ext else '(no ext)'
            
        s += '\n %3d  %10s  files' % ( len(ext2filenames[ext]), x)
#         
#         if len(ext) > 4:
#             logger.warn(ext2filenames[ext])
    logger.info(s)
        
    
    def check(ext, msg):
        if ext in ext2filenames:
            msg += '\nOffending files: '
            for f in ext2filenames[ext]:
                msg += '\n  %s ' % friendly_path(f)
        
            raise Exception(msg)
        
    check('.JPG', 'Use lower case "jpg". ')
    check('.jpeg', 'Use "jpg", not "jpeg". ')
    check('.JPEG', 'Use lower case "jpg", not "JPEG". ')
    