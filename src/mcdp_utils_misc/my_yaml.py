from ruamel import yaml  # @UnresolvedImport

def yaml_load(s):
    return yaml.load(s, yaml.RoundTripLoader)

def yaml_dump(s):
    return yaml.dump(s, Dumper=yaml.RoundTripDumper)