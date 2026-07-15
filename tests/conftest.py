import os

# Tests must not touch the real ~/.claude — disable auto-installation of the slash wrapper.
os.environ.setdefault("SPEC_FORGE_NO_SLASH", "1")
