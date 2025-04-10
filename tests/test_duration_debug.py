#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug the duration_compact function."""
import sys
import os
import importlib.util

# Load the module directly without importing
module_path = os.path.join(os.path.dirname(__file__), '../src/mcdp_utils_misc/duration_hum.py')
spec = importlib.util.spec_from_file_location("duration_hum", module_path)
duration_hum = importlib.util.module_from_spec(spec)
spec.loader.exec_module(duration_hum)

# Extract the function to test
duration_compact = duration_hum.duration_compact

# Test with various year values
for years in [1, 2, 3]:
    # Convert years to seconds directly using the same formula as in the function
    seconds = int(years * 365.242199 * 24 * 60 * 60)
    result = duration_compact(seconds)
    print(f"{years} years ({seconds} seconds) => '{result}'")
    
    # Calculate what the function does
    minutes, seconds_rem = divmod(seconds, 60)
    hours, minutes_rem = divmod(minutes, 60)
    days, hours_rem = divmod(hours, 24)
    years_calc, days_rem = divmod(days, 365.242199)
    print(f"  Internal calculation: {years_calc} years, {days_rem} days, {hours_rem} hours")