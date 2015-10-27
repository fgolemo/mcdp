import os
from setuptools import setup, find_packages

version = "1.0"

setup(name='mocdp',
      url='http://github.com/AndreaCensi/mcdp',
      description='Monotone Co-Design Problems',
      long_description='',
      package_data={'':['*.*', '*.mcdp', '*.cdp', '*.png']},
      keywords="",
      license="",

      classifiers=[
        'Development Status :: 4 - Beta',
      ],

      version=version,

      download_url=
        'http://github.com/AndreaCensi/mcdp/tarball/%s' % version,

      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[
        'ConfTools>=1.0,<2',
        'PyContracts>=1.2,<2',
        'quickapp', 
        'reprep',
        'gvgen',
        'pint',
        'watchdog',
        'networkx',
      ],
      tests_require=[
        'nose>=1.1.2,<2',
        'comptests',
        'compmake',
      ],
      entry_points={

         'console_scripts': [
            'mcdp_plot = cdpview:mcdp_plot_main',
            
        ]
      }
)

