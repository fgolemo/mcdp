import os
import shutil
from tempfile import mkdtemp
import warnings

from system_cmd.meat import system_cmd_result
from system_cmd.structures import CmdException
from contracts.utils import raise_wrapped, indent

class ConversionError(Exception):
    pass

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
        cmd += ['-strip']
        cmd += [out]
        try:
            res = system_cmd_result(cwd='.', cmd=cmd,
                     display_stdout=False,
                     display_stderr=False,
                     raise_on_error=True)
            
            if not os.path.exists(out):
                msg = "ImageMagick did not fail, but it didn't write the image it promised."
                msg += "\n"+indent(" ".join(cmd), " invocation: ") 
                msg += "\n"+ indent(res.stdout or "(no output)", '|', 'stdout: |')
                msg += "\n"+ indent(res.stderr or "(no output)", '|', 'stderr: |')
                where = 'problematic.pdf'
                msg += "\n I will copy the problematic pdf file to %s" % where
                shutil.copy(tmpfile, where)
                raise CmdException(msg)

        except CmdException as e:
            msg = 'I was not able to use Imagemagick to convert an image.'
            
            try: 
                version = system_cmd_result(cwd='.', cmd=['convert', '--version'],
                     display_stdout=False,
                     display_stderr=False,
                     raise_on_error=True)
                msg += '\n ImageMagick "convert" version:'
                msg += '\n' + indent(version.stdout, ' | ')
            except: 
                pass
            raise_wrapped(ConversionError, e, msg, compact=True)
        
        r = open(out,'rb').read()
        return r
    finally:
        shutil.rmtree(d)