from comptests.registrar import comptest_dynamic
from mcdp_hdb_mcdp.cli_load_all import define_load_all_jobs
from mcdp_utils_misc.dir_from_package_nam import dir_from_package_name
import os


@comptest_dynamic
def load_all(context):
    outdir = os.path.join('out/comptests/load_all')
    mcdp_data = dir_from_package_name('mcdp_data')
    dirname = os.path.join(mcdp_data, 'bundled.mcdp_repo')
    define_load_all_jobs(context, dirname, outdir, name_filter=None, errors_only=False)

# 
#     
# if __name__ == '__main__':
#     run_module_tests()