# -*- coding: utf-8 -*-
from mcdp_hdb.schema import Schema
from comptests.registrar import comptest, run_module_tests
from mcdp.constants import MCDPConstants
import yaml
from mcdp.logs import logger
from contracts.utils import indent
from mcdp_hdb.disk_map import DiskMap

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

    dm = DiskMap()
    dm.hint_extensions(s['images'], exts)

#     data = s.generate()
    
    d = 'contents'
    h0 = {'images': {'im1.jpg': d, 'im2.png': d, 'im2.jpg': d}}
    l('h0', yaml.dump(h0))
    
    data = dm.interpret_hierarchy(s, h0)
    l('data', yaml.dump(data))
    s.validate(data)
#     
#     dm1 = DiskMap()
#     h1 = dm1.create_hierarchy(s, data)
#     l('h1', yaml.dump(h1))

    h1 = dm.create_hierarchy(s, data)
    l('h1', yaml.dump(h1))


if __name__ == '__main__':
    run_module_tests()