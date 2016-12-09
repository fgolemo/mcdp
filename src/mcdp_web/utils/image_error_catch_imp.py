# -*- coding: utf-8 -*-
from .response import response_data


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
    
def response_image(request, s, size=(1024, 1024), color=(255,0,0)):
    # only use the
    maxwidth = 100
    s = break_lines(s, maxwidth)
    
    maxlines = 30
    lines = s.split("\n")
    if len(lines) > maxlines:
        lines = lines[-maxlines:]
    s = "\n".join(lines)
    
    data = create_image_with_string(s, size=size, color=color)
    return response_data(request=request, data=data, content_type='image/png')


def create_image_with_string(s, size, color):
    """ Returns string of png data """
    from PIL import Image
    # from PIL import ImageFont
    from PIL import ImageDraw
    img = Image.new("RGB", size, "white")

    draw = ImageDraw.Draw(img)
    draw.text((0, 0), s, color)  # , font=font)
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
