# -*- coding: utf-8 -*-
from contracts.utils import indent

from comptests.registrar import comptest, run_module_tests
from mcdp.constants import MCDPConstants
from mcdp.logs import logger
from mcdp_hdb.disk_map import DiskMap
from mcdp_hdb.disk_struct import ProxyDirectory, ProxyFile
from mcdp_hdb.schema import Schema
from mcdp_utils_misc import yaml_dump


def l(what, s):
    logger.info('\n' + indent(s, '%010s │  ' % what))

@comptest
def test_extension():
    exts = sorted(set(_.lower() for _ in MCDPConstants.exts_images))
    
    s = Schema()
    image = Schema()
    for ext in exts:
        image.bytes(ext, can_be_none=True) # and can be none
    s.hash('images', image)
    
    l('schema', s)

    dm = DiskMap(s)
    dm.hint_extensions(s['images'], exts)
    
    d = 'contents'
    h0 = ProxyDirectory(directories={'images':
                                     ProxyDirectory(files={'im1.jpg': ProxyFile(d), 
                                                           'im2.png': ProxyFile(d), 
                                                           'im2.jpg': ProxyFile(d)})})
    
    
    data = dm.interpret_hierarchy_(s, h0)
    l('data', yaml_dump(data))
    s.validate(data)

    h1 = dm.create_hierarchy_(s, data)
    l('h1', h1.tree())


    if h0.hash_code() != h1.hash_code():
        msg = 'They do not match'
        msg += '\n' + indent(h0.tree(), 'h0 ')
        msg += '\n' + indent(h1.tree(), 'h1 ')
        raise Exception(msg) 
    
    
if __name__ == '__main__':
    run_module_tests()