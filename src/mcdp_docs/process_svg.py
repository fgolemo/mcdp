#!/usr/bin/env python

from mcdp_utils_misc.locate_files_imp import locate_files
import os
from system_cmd import system_cmd_result
from mcdp_utils_misc.fileutils import create_tmpdir
from compmake.utils.friendly_path_imp import friendly_path
join = os.path.join
from decent_params.utils.script_utils import UserError, wrap_script_entry_point
import shutil


inkscape_cmd = 'inkscape'

mac = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'
if os.path.exists(mac):
    inkscape_cmd = mac

latex_cmd = 'pdflatex'
crop_cmd = 'pdfcrop'

from mcdp import logger

def process_svg_files(root, out, preamble):
    logger.info('root = %s' % root)
    logger.info('out = %s' % out)
    logger.info('preamble = %s' % preamble)
    if not os.path.exists(out):
        os.makedirs(out)
    logger.info('Looking for *.svg files...')
    svgs = locate_files(root, '*.svg')
    logger.info('%d found in %s' % (len(svgs), friendly_path(root)))
    
    for f in svgs:    
        basename, _ = os.path.splitext(os.path.basename(f))
        target = join(out, basename + '.pdf')
        
        if not needs_remake(f, target): 
            msg = 'The target %r is up to date.' % target
            logger.info(msg)
            
        else:
            msg = 'Will build target %r.' % target
            logger.info(msg)
            tmpdir = create_tmpdir('svg-%s' % basename)
            
            process_svg_file(f, target, preamble, tmpdir)

def needs_remake(src, target):
    if not os.path.exists(target):
        logger.debug('Target does not exist: %s' % target)
        return True
    target_time = os.path.getmtime(target)
    src_time = os.path.getmtime(src)
    src_is_newer = target_time < src_time
    if src_is_newer:
        logger.debug('Source is newer.')
    return  src_is_newer
        
def process_svg_file(filename, target, preamble, proc_dir):
    if not os.path.exists(proc_dir):
        try:
            os.makedirs(proc_dir)
        except:
            pass

    logger.debug('Copying SVG file to temp directory %s '% proc_dir)
    shutil.copy(filename, join(proc_dir, 'in.svg.tmp'))

    logger.debug('Running Inkscape.')
    cmd = [inkscape_cmd,
           '-D',
           '-z',
           '--file', join(proc_dir, 'in.svg.tmp'),
           '--export-pdf', join(proc_dir, 'out.pdf'),
           '--export-latex']

    system_cmd_result(cwd=proc_dir, cmd=cmd,
                      display_stdout=False,
                      display_stderr=False,
                      raise_on_error=True)
    
    assert os.path.exists(join(proc_dir, 'out.pdf'))
    assert os.path.exists(join(proc_dir, 'out.pdf_tex'))

    logger.debug('Creating template file..')
    # ok now we have the pdf and pdf_tex files ready.
    # Let's build the temp tex file to generate the figure
    s = r"""
\documentclass[]{article}
\usepackage{graphicx}
\usepackage{color}
\begin{document}
\pagestyle{empty}
\input{PREAMBLE}
\input{out.pdf_tex}
\end{document}
"""
    s = s.strip() 
    s = s.replace('PREAMBLE', os.path.realpath(preamble))

    fn = join(proc_dir, 'file.tex')
    with open(fn, 'w') as f:
        f.write(s)

    # compile
    logger.debug('Compile using latex..')
    cmd = [latex_cmd, 'file.tex']
    system_cmd_result(cwd=proc_dir, cmd=cmd,
                      display_stdout=False,
                      display_stderr=False,
                      raise_on_error=True)
    # crop
    logger.debug('Crop the pdf..')
    cmd = [crop_cmd, 'file.pdf', 'cropped.pdf']
    system_cmd_result(cwd=proc_dir, cmd=cmd,
                      display_stdout=False,
                      display_stderr=False,
                      raise_on_error=True)
    
    
    logger.debug('Copying to target %r..' % target)
    shutil.copy(join(proc_dir, 'cropped.pdf'), target)

def main(args):
    if len(args) != 3:
        msg = 'Usage: %prog dir_input dir_output preamble'
        raise UserError(msg)
    din, dout, preamble = args
    process_svg_files(din, dout, preamble)
    return 0


if __name__ == '__main__':
    wrap_script_entry_point(main, logger)
