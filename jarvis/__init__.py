# Top-level package for the JARVIS project
# This file makes the inner `jarvis` directory (d:\\jarvis-personal-assistant\\jarvis\\jarvis) importable as `jarvis`.
# It extends the package path to include the nested folder, preserving existing submodule structure.
import os

# Directory containing the nested package
_inner_pkg_dir = os.path.join(os.path.dirname(__file__), 'jarvis')
if os.path.isdir(_inner_pkg_dir):
    __path__.append(_inner_pkg_dir)

