from distutils.core import setup
setup(
  name = 'buttonwood',
  packages = ['buttonwood'],
  version = '1.0',
  license='MIT',
  description = 'Buttonwood is a python software package created to help quickly create, (re)build, or analyze markets, market structures, and market participants.',
  author = 'Peter F. Nabicht',
  author_email = 'nabicht@gmail.com',
  url = 'https://github.com/nabicht/Buttonwood',
  download_url = 'https://github.com/nabicht/Buttonwood/archive/v1.0.0.tar.gz',
  keywords = ['markets', 'finance', 'electronic markets', 'microstructure', 'market analysis'],
  install_requires=[
          'nose',
          'cdecimal',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Office/Business :: Financial',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7'
  ],
)