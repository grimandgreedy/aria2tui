#!/bin/python
# -*- coding: utf-8 -*-
"""
aria2c_utils.py - DEPRECATED: Compatibility shim

This module is maintained for backward compatibility.
All functionality has been moved to the aria2tui.utils.aria2c package.

Please update your imports to use:
    from aria2tui.utils.aria2c import *

This compatibility shim will be removed in a future version.

Author: GrimAndGreedy
License: MIT
"""

import warnings

# Issue deprecation warning (only shown once per interpreter session)
warnings.warn(
    "aria2c_utils is deprecated. Use 'from aria2tui.utils.aria2c import *' instead. "
    "This compatibility shim will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from the new package for backward compatibility
from aria2tui.utils.aria2c import *

# Also re-export module-level config variables
from aria2tui.utils.aria2c import config, url, port, token
