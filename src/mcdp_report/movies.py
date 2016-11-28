# -*- coding: utf-8 -*-
import os
from tempfile import mkdtemp

from contracts import contract
from mocdp import logger

from .utils import safe_makedirs

__all__ = [
    'create_movie_from_png_sequence',
]

@contract(sequence='list(str)', out='str')
def create_movie_from_png_sequence(sequence, out, fps=1.0):
    """ Creates an MP4 out of the list of png data """
    
    safe_makedirs(os.path.dirname(out))

    tmpdir = mkdtemp()
    for i, frame in enumerate(sequence):
    
        fn = os.path.join(tmpdir, '%05d.png' % i)
        with open(fn, 'w') as fi:
            fi.write(frame)

    try:
        import procgraph_mplayer  # @UnusedImport

    except ImportError as e:
        logger.error('Cannot use Procgraph to create video.')
        logger.error(e)
        logger.info('The frames are in the directory %s' % tmpdir)
    else:
        join_video_29_fixed(output=out, dirname=tmpdir,
                            pattern='.*.png', fps=fps)

def join_video_29_fixed(output, dirname, pattern, fps):
    """ 
        Note that the pattern is a Python regex:
        
        pg-video-join -d anim-simple/ -p '*.png' -o anim-simple-collate.mp4 --fps 1 
        
    """
    from procgraph.core.registrar_other import register_model_spec
    from procgraph import pg

    register_model_spec("""
--- model join_video_helper_29
config output
config dirname
config pattern
config images_per_second

|files_from_dir dir=$dirname regexp=$pattern fps=$images_per_second| \
--> |imread_rgb| \
--> |fix_frame_rate fps=29.97| \
--> |mencoder quiet=1 file=$output timestamps=0|
    
    """)
    params = dict(dirname=dirname, 
                  pattern=pattern, 
                  output=output,
                  images_per_second=fps)
    pg('join_video_helper_29', params)

