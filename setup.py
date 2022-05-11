from setuptools import setup, Extension

CPATH = "pypathfinder\\fast"
CPACK = CPATH.replace("\\", ".")

ext1 = Extension(f"{CPACK}.ctools", [f"{CPATH}\\ctools.c"])
ext = [ext1]

setup(
    ext_modules=ext
)