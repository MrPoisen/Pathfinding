from setuptools import setup, Extension

CPATH = "pypathfinder\\fast"
CPACK = CPATH.replace("\\", ".")

ext1 = Extension(f"{CPACK}.ctools", [f"{CPATH}\\ctools.c"])
ext2 = Extension(f"{CPACK}.citools", [f"{CPATH}\\citools.c"])
ext = [ext1, ext2]

setup(
    ext_modules=ext
)