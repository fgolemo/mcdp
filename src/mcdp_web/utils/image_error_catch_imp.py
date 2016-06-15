from .response import response_data
import traceback


def png_error_catch(f, request):
    try:
        return f()
    except Exception as e:
        s = traceback.format_exc(e)

        try:
            print(s)
        except UnicodeEncodeError:
            pass

        s = str(s)

        return response_image(request, s)

def response_image(request, s):
    from PIL import Image
    # from PIL import ImageFont
    from PIL import ImageDraw
    img = Image.new("RGB", (512, 512), "white")

    draw = ImageDraw.Draw(img)
#         font = ImageFont.truetype("sans-serif.ttf", 16)
#         font = ImageFont.truetype("arial.ttf", 16)

    draw.text((0, 0), s, (255, 0, 0))  # , font=font)
    data = get_png(img)

    return response_data(request=request, data=data, content_type='image/png')

def get_png(image):
    """ Gets png data from PIL image """
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png') as tf:
        fn = tf.name
        image.save(fn)
        with open(fn, 'rb') as f:
            data = f.read()
        return data
