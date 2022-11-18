from setuptools import setup

setup(
    name="chime_pipeline",
    version="0.1.0",
    description="A pipeline to generate wideband TOAs from CHIME fold mode data.",
    author="Abhimanyu Susobhanan, Gabriella Agazie, David Kaplan",
    author_email="abhimanyu.susobhanan@nanograv.org",
    url="https://github.com/abhisrkckl/chime_pipeline",
    license="GNU GPL v3",
    packages=["chime_pipeline"],
    package_dir={"chime_pipeline": "chime_pipeline"},
    scripts=["scripts/chime2wbtoa.py", "scripts/chime_convert_and_tfzap.psh"],
    install_requires=[
        "astropy",
        "pint-pulsar",
        "PulsePortraiture"
    ]
)
