<h1 align="center">sqlinks</h1> <br>
<p align="center">
  <a href="">
    <img alt="sqlinks" title="sqlinks" src="images/link-logo.png" width="250">
  </a>
</p>

<p align="center">
  Diagram your data pipelines.
</p>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Features](#features)
- [Example](#example)
- [Getting started](#getting-started)
- [Feedback](#feedback)
- [Acknowledgments](#acknowledgments)
- [Dev](#dev)
- [Deflation](#deflation)
  - [](#)
  - [PyPI](#pypi)

## Introduction

Documenting data pipelines is hard. Not only is it complex, but it's also time consuming. When working with big teams it becomes near impossible; documentation is out of date as soon as it's completed as there's continual change. **sqlinks** hopes to remedy this by allowing you to generate flow diagrams programatically. This allows for reproducable and clear diagrams that, by using [diagrams.net](diagrams.net), are also easily accessible by non-technical users.


## Features

- 👍 Generate flow diagrams from simple CTAS statements
- 👍 Visualise interactions of schemas, tables & columns

To come...
- ⏳ Functionality for complex CTAS statements, CTEs, INSERT statements etc.
- ⏳ Customisation via config files


## Example

Coming soon...

## Getting started

Install **sqlinks** using **pip**:

```pip install sqlinks```


When installed, run **sqlinks** against your current directory using the following:

```python -m sqlinks```

To view all available command line options use:

```python -m sqlinks --help```


## Feedback

Feel free to reach out on [LinkedIn](https://www.linkedin.com/in/dominic-herriott/) and please use [GitHub Issues](https://github.com/domherriott/sqlinks/issues) for feature requests! :grinning:

## Acknowledgments

Thanks to all those who have contributed and helped build the packages this is built on.

Special thanks to the developers at [diagrams.net](diagrams.net)!

## Dev
run `pre-commit install` to set up the git hook scripts


## Deflation
https://drawio-app.com/extracting-the-xml-from-mxfiles/

https://jgraph.github.io/drawio-tools/tools/convert.html

###

Build dist files
`python setup.py sdist bdist_wheel`

Push to PyPI
`python -m twine upload --repository testpypi dist/*`


### PyPI
https://pypi.org/project/sqlinks/0.0.1/
