
__all__ = [
    'yaml_load', 
    'yaml_dump',
]

if True:
    from ruamel import yaml  # @UnresolvedImport
    # XXX: does not represent None as null, rather as '...\n'
    def yaml_load(s):
        if s.startswith('...'):
            return None
        return yaml.load(s, yaml.RoundTripLoader)
    
    def yaml_dump(s):
        return yaml.dump(s, Dumper=yaml.RoundTripDumper)
else:
    import yaml  # @Reimport
    def yaml_load(s):
        return yaml.load(s)
    
    def yaml_dump(s):
        return yaml.dump(s)