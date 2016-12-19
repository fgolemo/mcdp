# -*- coding: utf-8 -*-
from .mcdp_render import mcdp_render_main
from .mcdp_render_manual import mcdp_render_manual_main


# annoying warning from BS4
import bs4
import logging
logging.getLogger("chardet.universaldetector").setLevel(logging.CRITICAL)