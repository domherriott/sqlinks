from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "Streaming video data via networks"
LONG_DESCRIPTION = (
    "A package that allows to build simple streams of video, audio and camera data."
)

# Setting up
setup(
    name="flowsql",
    version=VERSION,
    author="Dominic Herriott",
    author_email="dominicherriott@outlook.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=["python", "documentation", "sql"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
