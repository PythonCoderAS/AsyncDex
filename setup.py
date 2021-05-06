from setuptools import setup
from asyncdex import version

setup(
    name='AsyncDex',
    version=version,
    packages=['asyncdex'],
    url='https://github.com/PythonCoderAS/AsyncDex',
    license='MIT',
    author='PythonCoderAS',
    author_email='pokestarfan@yahoo.com',
    description='Async MangaDex library',
    install_requires=["aiohttp"]
)
