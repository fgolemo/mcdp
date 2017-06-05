# -*- coding: utf-8 -*-
from mcdp_report.html import ast_to_html
from mcdp_utils_misc.fileutils import get_mcdp_tmp_dir
import os
import shutil
from system_cmd import CmdException, system_cmd_result
from tempfile import mkdtemp

from .minimal_doc import get_minimal_document


def crop_pdf(pdf, margins=0):
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'crop_pdf()'
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    
    try:
        f_pdf = os.path.join(d, 'file.pdf')
        with open(f_pdf, 'w') as f:
            f.write(pdf)
        f_pdf_crop = os.path.join(d, 'file_crop.pdf')
        cmd = [
            'pdfcrop', 
            '--margins', 
            str(margins), 
            f_pdf, 
            f_pdf_crop,
        ]
        system_cmd_result(
                d, cmd,
                display_stdout=False,
                display_stderr=False,
                raise_on_error=True)
    
        with open(f_pdf_crop) as f:
            data = f.read()
        return data
    finally:
        shutil.rmtree(d)
        

def get_ast_as_pdf(s, parse_expr):
    s = s.replace('\t', '    ')
    contents = ast_to_html(s,
                       ignore_line=None, parse_expr=parse_expr,
                       add_line_gutter=False)
    html = get_minimal_document(contents)
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'get_ast_as_pdf()'
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    
    try:
        f_html = os.path.join(d, 'file.html')
        with open(f_html, 'w') as f:
            f.write(html)
            
        try:
            f_pdf = os.path.join(d, 'file.pdf')
            cmd= ['wkhtmltopdf','-s','A1',f_html,f_pdf]
            system_cmd_result(
                    d, cmd, 
                    display_stdout=False,
                    display_stderr=False,
                    raise_on_error=True)
    
            with open(f_pdf) as f:
                data = f.read()
            
            data = crop_pdf(data, margins=0)
    
            return data
        except CmdException as e:
            raise e
    finally:
        shutil.rmtree(d)
