from setuptools import setup, find_packages

VERSION = "0.0.2"
DESCRIPTION = "Streaming video data via networks"
LONG_DESCRIPTION = "Documenting data pipelines is hard. Not only is it complex, but it's also time consuming. When working with big teams it becomes near impossible; documentation is out of date as soon as it's completed as there's continual change. **sqlinks** hopes to remedy this by allowing you to generate flow diagrams programatically. This allows for reproducable and clear diagrams that, by using [diagrams.net](diagrams.net), are also easily accessible by non-technical users."

# Setting up
setup(
    name="sqlinks",
    version=VERSION,
    author="Dominic Herriott",
    author_email="dominicherriott@outlook.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["sqlparse", "sql_metadata", "jinja2"],
    keywords=["python", "documentation", "sql"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    package_data={"sqlinks": ["app/templates/*.xml"]},
)
