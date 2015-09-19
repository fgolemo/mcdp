import os
from setuptools import setup, find_packages

version = "1.0"

setup(name='mocdp',
      url='',
      description='',
      long_description='',
      package_data={'':['*.*']},
      keywords="",
      license="",

      classifiers=[
        'Development Status :: 4 - Beta',
      ],

      version=version,

      download_url=
        'http://github.com/AndreaCensi/mocdp/tarball/%s' % version,

      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[
        'ConfTools>=1.0,<2',
        'PyContracts>=1.2,<2',
        'quickapp', 
      ],
      tests_require=['nose>=1.1.2,<2'],
      entry_points={

         'console_scripts': [
            # 'popt_plot_cgraph = procgraph_optimize.programs:plot_cgraph',
            
        ]
      }
)

