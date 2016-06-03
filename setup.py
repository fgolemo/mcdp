import os
from setuptools import setup, find_packages

def get_version(filename):
    import ast
    version = None
    with file(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version

version = get_version(filename='src/mocdp/__init__.py')

setup(name='PyMCDP',
      url='http://github.com/AndreaCensi/mcdp',
      maintainer="Andrea Censi",
      description='PyMCDP is an nterpreter and solver for Monotone Co-Design Problems',
      long_description='',
      package_data={'':['*.*', '*.mcdp', '*.cdp', '*.png']},
      keywords="Optimization",
      license="MIT",
      classifiers=[
        'Development Status :: 4 - Beta',
      ],
      version=version,

      download_url=
        'http://github.com/AndreaCensi/mcdp/tarball/%s' % version,

      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[
        #'ConfTools>=1.0,<2',
        #'PyContracts>=1.2,<2',
        # '#quickapp', 
        # 'reprep',
        # 'gvgen',
        'pint',
        'watchdog',
        'networkx',
        'PyContracts>=1.7.6',
        'ConfTools>=1.7',
        'QuickApp>=1.2',
        'RepRep>=2.9.3',
        # 'gvgen==0.9.1',
      ],
      dependency_links  = [
          'https://github.com/AndreaCensi/contracts/archive/env_fault.zip#egg=PyContracts',
          'https://github.com/AndreaCensi/conf_tools/archive/env_fault.zip#egg=ConfTools',
          #'https://github.com/AndreaCensi/quickapp/archive/env_fault.zip#egg=QuickApp',
          'git+https://github.com/AndreaCensi/quickapp.git@env_fault#egg=QuickApp',
          'https://github.com/AndreaCensi/reprep/archive/env_fault.zip#egg=RepRep',
          # 'https://github.com/AndreaCensi/gvgen/archive/master.zip#egg=gvgen-0.9.1',
      ],

      tests_require=[
        'nose>=1.1.2,<2',
        'comptests',
        'compmake',
      ],

      entry_points={
         'console_scripts': [
            'mcdp_plot = cdpview:mcdp_plot_main',
            'mcdp_solve = cdpview:mcdp_solve_main',
            'mcdp-plot = cdpview:mcdp_plot_main',
            'mcdp-solve = cdpview:mcdp_solve_main',
            'mcdp-web = mcdp_web:mcdp_web_main',
        ]
      }
)

