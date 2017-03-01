# -*- coding: utf-8 -*-
import base64

from bs4.element import Tag

from contracts import contract



@contract(data_format=str, data=str, download=str)
def create_a_to_data(download, data_format, data):
    """ Returns a tag with base64 encoded data """
    assert data_format in ['pdf', 'png']
    from mcdp_web.images.images import (get_mime_for_format)
    mime = get_mime_for_format(data_format)
    encoded = base64.b64encode(data)
    href = 'data:%s;base64,%s' % (mime, encoded)
    attrs = dict(href=href, download=download)
    return Tag(name='a', attrs=attrs)


def create_img_png_base64(png, **attrs):
    encoded = base64.b64encode(png)
    src = 'data:image/png;base64,%s' % encoded
    attrs = dict(**attrs)
    attrs['src'] =src
    return Tag(name='img', attrs=attrs)
