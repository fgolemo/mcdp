from .response import response_data
import traceback

#
#
# def png_error_catch(f, request):
#     from mocdp import logger
#     try:
#         return f()
#     except Exception as e:
#         s = traceback.format_exc(e)
#
#         try:
#             logger.error(s)
#         except UnicodeEncodeError:
#             pass
#
#         s = str(s)
#
#         return response_image(request, s)

def response_image(request, s):

    # only use the
    maxlines = 30
    lines = s.split("\n")
    if len(lines) > maxlines:
        lines = lines[-maxlines:]
    s = "\n".join(lines)

    data = create_image_with_string(s, size=(512, 512), color=(255, 0, 0))
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
