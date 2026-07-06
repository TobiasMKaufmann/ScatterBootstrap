"""
Used to find compiled C extension files in a platform-independent way.
Usually used by Python wrappers to load the correct shared library.
"""

import os
import sys
import glob


def find_library(base_name, current_dir=None):
    """Find the compiled library file, handling platform-specific naming.

    Searches for library files with various extensions (.so, .pyd, .dll) and
    naming patterns (simple names and platform-specific setuptools names).
    """
    if current_dir is None:
        current_dir = os.path.dirname(__file__)

    # Build list of all possible patterns to search, in priority order
    # Windows: .pyd and .dll extensions
    # Linux/Mac: .so extension
    extension_patterns = []
    if sys.platform == "win32":
        extension_patterns = ["pyd", "dll"]
    else:
        extension_patterns = ["so"]

    # # Collect all candidate files
    # candidates = []
    # for ext in extension_patterns:
    #     # Pattern matches: any file containing base_name with the correct extension
    #     pattern = os.path.join(current_dir, f'*{base_name}*.{ext}')
    #     candidates.extend(glob.glob(pattern))

    patterns = [
        f"{base_name}",
        f"{base_name}.cpython-*-*",
        f"{base_name}.cpython-*-darwin",
        f"{base_name}.cp*-win_*",
    ]

    candidates = []
    for ext in extension_patterns:
        for pattern in patterns:
            search_pattern = os.path.join(current_dir, ".".join([pattern, ext]))
            candidates.extend(glob.glob(search_pattern))

    # Sort by filename length (prefer simpler names)
    candidates.sort(key=lambda x: len(os.path.basename(x)))

    # Return the first match or raise error
    if candidates:
        return candidates[0]

    raise FileNotFoundError(
        f"Could not find compiled library '{base_name}' in {current_dir}.\n"
        f"Expected files like: {base_name}.so, {base_name}.pyd, or platform-specific variants.\n"
        f"Make sure to run 'pip install -e .' first."
    )
