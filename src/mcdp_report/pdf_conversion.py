import os
import shutil
from tempfile import mkdtemp
import warnings

from system_cmd.meat import system_cmd_result
from system_cmd.structures import CmdException


def png_from_pdf(pdf_data, density):
    """ Converts a pdf to png with the given density """
    d = mkdtemp()
    try:
        tmpfile = os.path.join(d, 'file.pdf')
        with open(tmpfile, 'wb') as f:
            f.write(pdf_data)
        
        out = os.path.join(d, 'file.png')
    
        cmd = [
            'convert',
            '-density', str(density), 
            tmpfile, 
            '-background', 'white',
            '-alpha','remove',
            '-alpha','off', 
        ]
        shave = True
        if shave:
            warnings.warn('Using shave to fix some bug in imagemagic')
            cmd += ['-shave', '1']
        cmd += [out]
        try:
            system_cmd_result(cwd='.', cmd=cmd,
                     display_stdout=False,
                     display_stderr=False,
                     raise_on_error=True)

        except CmdException:
            raise
        
        r = open(out,'rb').read()
        return r
    finally:
        shutil.rmtree(d)