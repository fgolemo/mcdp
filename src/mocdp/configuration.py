from conf_tools import ConfigMaster


__all__ = [
    'get_conftools_mocdp_config',
    'get_conftools_posets',
    'get_conftools_dps',
    'get_conftools_nameddps',
]

class MOCDPConfig(ConfigMaster):
    def __init__(self):
        ConfigMaster.__init__(self, 'MOCDPConfig')

        from mocdp.posets import Poset
        from mocdp.dp import PrimitiveDP

        self.add_class_generic('posets', '*.posets.yaml', Poset)
        self.add_class_generic('dps', '*.dps.yaml', PrimitiveDP)

        from mocdp.comp.interfaces import NamedDP
        self.add_class_generic('nameddps', '*.nameddps.yaml', NamedDP)


get_conftools_mocdp_config = MOCDPConfig.get_singleton

def get_conftools_nameddps():
    return get_conftools_mocdp_config().nameddps

def get_conftools_posets():
    return get_conftools_mocdp_config().posets

def get_conftools_dps():
    return get_conftools_mocdp_config().dps
