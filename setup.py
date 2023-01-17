from setuptools import setup
import versioneer

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    scripts=["scripts/chimerawb", "scripts/chime_convert_and_tfzap.psh"],
)
