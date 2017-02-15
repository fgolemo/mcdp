# -*- coding: utf-8 -*-
from .response import response_data
from PIL import ImageFont
import os
from mcdp import logger


def break_lines(s, maxwidth):
    lines = s.split("\n")
    lines2 = []
    for l in lines:
        while len(l) > maxwidth:
            part = l[:maxwidth] + '->'
            lines2.append(part) 
            l = '->' + l[maxwidth:]
        lines2.append(l)
    return "\n".join(lines2)
    
def response_image(request, s, size=(1024, 1024), color=(255,0,0), fontsize=10):
    # only use the
    maxwidth = 100
    s = break_lines(s, maxwidth)
    
    maxlines = 30
    lines = s.split("\n")
    if len(lines) > maxlines:
        lines = lines[-maxlines:]
    s = "\n".join(lines)
    
    data = create_image_with_string(s, size=size, color=color, fontsize=fontsize)
    return response_data(request=request, data=data, content_type='image/png')


def create_image_with_string(s, size, color, fontsize=10):
    """ Returns string of png data """
    from PIL import Image
    # from PIL import ImageFont
    from PIL import ImageDraw
    img = Image.new("RGB", size, "white")

    draw = ImageDraw.Draw(img)
#     font = ImageFont.truetype('FreeMono', 10)
    options = [
        '/usr/local/texlive/2015/texmf-dist/fonts/truetype/public/gnu-freefont/FreeMono.ttf',
        '/usr/share/fonts/truetype/freefont/FreeMono.ttf']
    for f in options:
        if os.path.exists(f):
            break
    else:
        logger.info('Could not find any font in %r' % options)
    
     
    font = ImageFont.truetype(f, fontsize)
    draw.text((0, 0), s, color, font=font)
    data = get_png(img)
    return data


def get_png(image):
    """ Gets png data from PIL image """
    import tempfile
    from PIL import Image
    Image.DEBUG = False

    with tempfile.NamedTemporaryFile(suffix='.png') as tf:
        fn = tf.name
        image.save(fn)
        with open(fn, 'rb') as f:
            data = f.read()
        return data
