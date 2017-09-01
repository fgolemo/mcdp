import os

from setuptools import find_packages, setup


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version

version = get_version(filename='src/mcdp/branch_info.py')

name = 'PyMCDP'

setup(name=name,
      url='http://github.com/AndreaCensi/mcdp',
      maintainer="Andrea Censi",
      maintainer_email="acensi@ethz.ch",
      description='PyMCDP is an interpreter and solver for Monotone Co-Design Problems',
      long_description='',
      #package_data={'':['*.*', '*.mcdp*', '*.js', '*.png', '*.css']},

      # without this, the stuff is included but not installed
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
        'decorator>=4.1.0',
        'networkx',
        'pyramid',
        'pyramid_jinja2',
        #'pyramid_chameleon',
        'pyramid_debugtoolbar',
        'bs4',
        'nose',
        'PyContracts>=1.7.6',
        'ConfTools>=1.7', # even if implied
        'comptests', # xxx: now it's always needed
        'RepRep>=2.9.3',
        'DecentLogs',
        'QuickApp>=1.2',
        'compmake',
          'psutil',
          'setproctitle',
        'markdown',
        'bcrypt',
        'waitress',
        'lxml',
        'junit_xml',
        'gitpython',
        'authomatic',
        'webtest',
        'ruamel.yaml',
        'python-dateutil',
      ],
      # This avoids creating the egg file, which is a zip file, which makes our data
      # inaccessible by dir_from_package_name()
      zip_safe = False,
      dependency_links  = [
          # 'https://github.com/AndreaCensi/contracts/archive/env_mcdp.zip#egg=PyContracts',
          # 'https://github.com/AndreaCensi/conf_tools/archive/env_fault.zip#egg=ConfTools',
          #'https://github.com/AndreaCensi/quickapp/archive/env_fault.zip#egg=QuickApp',
          # 'git+https://github.com/AndreaCensi/quickapp.git@env_mcdp#egg=QuickApp',
          # 'https://github.com/AndreaCensi/reprep/archive/env_mcdp.zip#egg=RepRep',
          # 'https://github.com/AndreaCensi/gvgen/archive/master.zip#egg=gvgen-0.9.1',
      ],

      tests_require=[
        'nose>=1.1.2,<2',
        'comptests',
      ],

      entry_points={
          'paste.app_factory': ['app=mcdp_web:app_factory'],

         'console_scripts': [
            'mcdp-plot = mcdp_cli:mcdp_plot_main',
            'mcdp-solve = mcdp_cli:mcdp_solve_main',
            'mcdp-web = mcdp_web:mcdp_web_main',
            'mcdp-eval = mcdp_cli:mcdp_eval_main',
            'mcdp-render = mcdp_docs:mcdp_render_main',
            'mcdp-render-manual = mcdp_docs:mcdp_render_manual_main',
            'mcdp-depgraph = mcdp_depgraph:mcdp_depgraph_main',
            'mcdp-load-all = mcdp_hdb_mcdp:mcdp_load_all_main',
        ]
      }
)
