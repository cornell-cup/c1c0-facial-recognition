import os

# FIXME: Currently AUTHORS gets saved as the license automatically by
#  setuptools. This isn't a problem, but can lead to future confusion.
from typing import Tuple

_env_falsey_vals = ['n', 'no', 'false', '0']
"""
These values are used to test against potential environment variable values
that default to being true.
"""
name = 'r2_facial_recognition'

meta = {
    'name': name,
    'backup_packages': {

    },  # used to find packages iff find_packages fails/is unavailable
    'readme': 'README.rst',
    'version': f'{name}/__init__.py',
    'authors': 'AUTHORS',
    'setup_requires': [
        'wheel',
    ],
    'long_description_content_type': 'text/x-rst',
}
"""
Various meta values used in the configuration.
name -
    Used to determine the name of the module and the folder the source code
    resides in.
backup_packages -
    Used iff find_packages fails or is unavailable.
readme -
    A readme containing a short and long description of the package.
version -
    Path to a python file that contains a line formatted as
    `__version_info__ = (#,#,#)`
authors -
    File containing the name, email, and website separated by newlines.
"""

# Try to import setuptools if PYTHON_USE_SETUPTOOLS is truthy or unset.
try:
    if os.environ.get('PYTHON_USE_SETUPTOOLS', '').lower() in _env_falsey_vals:
        raise ImportError
    # noinspection PyUnresolvedReferences
    from setuptools import setup, find_packages
    SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    SETUPTOOLS = False


def _load_authors(authors_file) -> Tuple[str, str, str]:
    """
    Opens the file given by meta['authors'] and assumes that the name, email,
    and website are separated by newlines.

    RETURNS
    -------
    -
        Either the name, email, and website or 3 error strings. Always a tuple
         of size 3 strings.
    """
    f = open(authors_file, 'r')
    try:
        author_data = f.read().split('\n')
        return author_data[0], author_data[1], author_data[2]
    except IndexError:
        e = 'Error retrieving Authors (Malformed)'
        return e, e, e
    finally:
        f.close()


_packages = find_packages() if SETUPTOOLS else meta['backup_packages']
print('SETUPTOOLS=', SETUPTOOLS)
print('packages=', _packages)


def readme(readme_file: str) -> str:
    """
    Opens the readme file given my `meta`.

    PARAMETERS
    ----------
    readme_file
        The name of the readme file. Do not give the absolute path.
    RETURNS
    -------
    -
        The contents of the readme.
    """
    with open(os.path.join(os.path.dirname(__file__), readme_file), 'r') as f:
        return f.read()


def get_short_description(_readme: str) -> str:
    """
    Takes the readme raw string and grabs the short description from it.
    Does not throw an exception if the short description is not found.
    If the short description is not found, 'No description found.' is returned.

    PARAMETERS
    ----------
    _readme
        The raw readme string.
    RETURNS
    -------
    -
        The short description as a str.
    """
    try:
        lines = _readme.split('\n')
        idx = -1
        for i in range(len(lines)):
            if lines[i].startswith(name):
                # 2 indexes forward because of rst formatting
                idx = i+2
                break
        if idx != -1:
            return lines[idx]
    except:
        pass
    return 'No description found.'


def get_version(version_file):
    """
    Grabs the version from the version_file str path. Expected to be formatted
    as `__version__ = (#,#,#)`.

    PARAMETERS
    ----------
    version_file
        The path to the file the version is located in.

    RETURNS
    -------
    -
        The version as a period separated string. For example, '1.2.3'.
    """
    # Inspired by https://stackoverflow.com/a/7071358
    import re
    ver_str_line = open(version_file, 'rt').read()
    vsre = r'__version_info__ *= *\( *(\d+) *, *(\d+) *, *(\d+) *\)'
    mo = re.search(vsre, ver_str_line, re.M)
    if mo:
        vertup = mo.group(1), mo.group(2), mo.group(3)
    else:
        raise RuntimeError('Unable to find version string in %s.' %
                           (version_file,))
    ver_str = '.'.join(vertup)
    return ver_str


def _setup(meta_):
    print('name=', name)
    long_description = readme(meta_['readme'])
    short_description = get_short_description(long_description)
    print('short_description=', short_description)
    author, author_email, url = _load_authors(meta_['authors'])
    print('author=', author)
    print('author_email=', author_email)
    print('url=', url)
    version = get_version(meta_['version'])
    print('version=', version)
    setup(
        name=name,
        version=version,
        author=author,
        author_email=author_email,
        url=url,
        description=short_description,
        long_description=long_description,
        packages=_packages,
        setup_requires=meta_['setup_requires'],
        license='',
        long_description_content_type=meta_['long_description_content_type'],
    )


if __name__ == '__main__':
    _setup(meta)
