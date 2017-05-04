from setuptools import setup, find_packages
setup(
    name="librobinson",
    version="0.2.1",
    packages=find_packages(),
    scripts=[
        'robinson/booknames.py',
        'robinson/book.py',
        'robinson/chapter.py',
        'robinson/convert.py',
        'robinson/__init__.py',
        'robinson/kind.py',
        'robinson/reader.py',
        'robinson/readwhat.py',
        'robinson/robinson.py',
        'robinson/robinsontags.py',
        'robinson/variant.py',
        'robinson/verse.py',
        'robinson/word.py',
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    #install_requires=['docutils>=0.3'],

    package_data={
        # If any package contains *.txt or *.md files, include them:
        '': ['*.txt', '*.md'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author="Ulrik Sandborg-Petersen",
    author_email="ulrikp@scripturesys.com",
    description="A library to parse and convert the New Testament Greek files of Dr. Maurice A. Robinson",
    license="MIT",
    keywords="Maurice A. Robinson, New Testament Greek, parse, convert",
    url="http://github.com/byztxt/librobinson"

    # could also include long_description, download_url, classifiers, etc.
)
