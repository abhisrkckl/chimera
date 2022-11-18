from setuptools import setup

setup(
    name="chimera-pulsar",
    version="0.1.0",
    description="A pipeline to generate wideband TOAs from CHIME fold mode data.",
    author="Abhimanyu Susobhanan, Gabriella Agazie, David Kaplan",
    author_email="abhimanyu.susobhanan@nanograv.org",
    url="https://github.com/abhisrkckl/chime_pipeline",
    license="GNU GPL v3",
    packages=["chimerawb"],
    package_dir={"chimerawb": "chimerawb"},
    scripts=["scripts/chimerawb", "scripts/chime_convert_and_tfzap.psh"],
    install_requires=[
        "astropy",
        "pint-pulsar",
        "PulsePortraiture"
    ]
)
