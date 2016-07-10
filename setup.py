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

name = 'PyMCDP'

setup(name=name,
      url='http://github.com/AndreaCensi/mcdp',
      maintainer="Andrea Censi",
      maintainer_email="andrea@censi.org",
      description='PyMCDP is an interpreter and solver for Monotone Co-Design Problems',
      long_description='',
      package_data={'':['*.*', '*.mcdp*', '*.js', '*.png', '*.css']},
      include_package_data=True,
      keywords="Optimization",
      license="GPLv2",
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
        # '#quickapp', 
        # 'reprep',
        'pint',
        'watchdog',
        'networkx',
        'pyramid',
        'pyramid_jinja2',
        'bs4',
        'nose',
        'PyContracts>=1.7.6',
        # 'ConfTools>=1.7',
        'RepRep>=2.9.3', 
        'DecentLogs',
        'QuickApp>=1.2',
        'compmake',
          'psutil',
          'setproctitle',
      ],
      dependency_links  = [
          # 'https://github.com/AndreaCensi/contracts/archive/env_mcdp.zip#egg=PyContracts',
          # 'https://github.com/AndreaCensi/conf_tools/archive/env_fault.zip#egg=ConfTools',
          #'https://github.com/AndreaCensi/quickapp/archive/env_fault.zip#egg=QuickApp',
          # 'git+https://github.com/AndreaCensi/quickapp.git@env_mcdp#egg=QuickApp',
          # 'https://github.com/AndreaCensi/reprep/archive/env_mcdp.zip#egg=RepRep',
          # 'https://github.com/AndreaCensi/gvgen/archive/master.zip#egg=gvgen-0.9.1',
      ],

      tests_require=[
#        'nose>=1.1.2,<2',
        'comptests',
      ],

      entry_points={
         'console_scripts': [
            # 'mcdp_plot = mcdp_cli:mcdp_plot_main',
            # 'mcdp_solve = mcdp_cli:mcdp_solve_main',
            'mcdp-plot = mcdp_cli:mcdp_plot_main',
            'mcdp-solve = mcdp_cli:mcdp_solve_main',
            'mcdp-web = mcdp_web:mcdp_web_main',
        ]
      }
)

