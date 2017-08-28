# -*- coding: utf-8 -*-
from .mcdp_render import mcdp_render_main
from .mcdp_render_manual import mcdp_render_manual_main
from .pipeline import render_complete

import git.cmd
from mcdp.constants import MCDPConstants
import getpass
git.cmd.log.disabled = True

from .logs import logger

if MCDPConstants.softy_mode:
    if getpass.getuser() == 'andrea':
        logger.error('Remember this might break MCDP')