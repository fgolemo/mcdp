from conf_tools import ConfigMaster

__all__ = [
    'get_conftools_mocdp_config',
    'get_conftools_posets',
]

class MOCDPConfig(ConfigMaster):
    def __init__(self):
        ConfigMaster.__init__(self, 'MOCDPConfig')

        from mocdp.defs import Poset
        self.add_class_generic('posets', '*.posets.yaml', Poset)


get_conftools_mocdp_config = MOCDPConfig.get_singleton

def get_conftools_posets():
    return get_conftools_mocdp_config().posets
