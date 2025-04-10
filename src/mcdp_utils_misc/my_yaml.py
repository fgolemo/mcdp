
"""
YAML utility functions that work consistently in Python 2 and 3.
"""

__all__ = [
    'yaml_load', 
    'yaml_dump',
]

try:
    # Try to use ruamel.yaml first (safer and round-trip capable)
    import sys
    from ruamel import yaml
    
    # Handle different ruamel.yaml API versions
    if sys.version_info[0] >= 3:
        # Modern API for Python 3
        try:
            # First try modern API
            yaml_modern = yaml.YAML(typ='rt')  # 'rt' for round-trip
            
            def yaml_load(s):
                """Load YAML safely with proper Python 3 support."""
                if s.startswith('...'):
                    return None
                # Use StringIO to parse string
                from io import StringIO
                stream = StringIO(s)
                return yaml_modern.load(stream)
            
            def yaml_dump(s):
                """Dump to YAML with proper Python 3 support."""
                from io import StringIO
                stream = StringIO()
                yaml_modern.dump(s, stream)
                return stream.getvalue()
                
        except (AttributeError, TypeError):
            # Fall back to legacy API for older ruamel.yaml
            def yaml_load(s):
                """Load YAML safely with proper Python 3 support using legacy API."""
                if s.startswith('...'):
                    return None
                return yaml.safe_load(s)
            
            def yaml_dump(s):
                """Dump to YAML with proper Python 3 support using legacy API."""
                return yaml.safe_dump(s)
    else:
        # Python 2 compatibility
        def yaml_load(s):
            """Load YAML safely with Python 2 support."""
            if s.startswith('...'):
                return None
            # RoundTripLoader preserves comments and formatting
            try:
                return yaml.load(s, Loader=yaml.RoundTripLoader)
            except AttributeError:
                return yaml.safe_load(s)
        
        def yaml_dump(s):
            """Dump to YAML with Python 2 support."""
            try:
                return yaml.dump(s, Dumper=yaml.RoundTripDumper)
            except AttributeError:
                return yaml.safe_dump(s)
        
except ImportError:
    # Fall back to PyYAML if ruamel.yaml is not available
    import yaml
    
    def yaml_load(s):
        """Load YAML safely with proper Python 3 support."""
        # SafeLoader is more secure in Python 3 than the default Loader
        return yaml.safe_load(s)
    
    def yaml_dump(s):
        """Dump to YAML with proper Python 3 support."""
        return yaml.safe_dump(s)