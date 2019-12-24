from distutils.core import setup
from setuptools import find_packages

setup(
  name = 'buttonwood',
  packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests",
                                    "*.exmaples", "*.examples.*", "examples.*", "examples"]),
  version = '2.0.1',
  license='MIT',
  description = 'Buttonwood is a python software package created to help quickly create, (re)build, or analyze markets, market structures, and market participants.',
  author = 'Peter F. Nabicht',
  author_email = 'nabicht@gmail.com',
  url = 'https://github.com/nabicht/Buttonwood',
  download_url = 'https://github.com/nabicht/Buttonwood/archive/v2.0.1.tar.gz',
  keywords = ['markets', 'finance', 'electronic markets', 'microstructure', 'market analysis'],
  install_requires=[],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Office/Business :: Financial',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ],
)