import setuptools


def get_version(path):
    with open(path, 'r') as f:
        for line in f.read().splitlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")


__version__ = get_version('fil3d/__init__.py')

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='Fil3D',
    version=__version__,
    description='A python package for building 3d filaments in (x,y,v)',
    long_description=long_description,
    url='https://lli1996.github.io/fil3d/',
    packages=['fil3d'],
    python_requires='>=3.6',
    install_requires=[
        'astropy',
        'matplotlib',
        'numpy>=0.19',
        'scipy',  # todo: possible sci image change
        # todo: correctly include the semi dependency of filfinder
    ]
)
