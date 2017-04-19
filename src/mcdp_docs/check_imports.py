import os
from conf_tools.utils.locate_files_imp import locate_files
from system_cmd.meat import system_cmd_result


d = 'src'
files = list(locate_files(directory=d, pattern='*.py'))

for f in files:
    if 'libraries' in f: continue
    f2 = os.path.relpath(f, d)
    f2 = f2.replace('/', '.')
    mod = f2.replace('.py', '')

    cwd = '.'
    cmd = ['python', '-c', 'import %s' % mod]
    print "python -c 'import %s'" % mod
    system_cmd_result(
            cwd, cmd,
            display_stdout=False,
            display_stderr=True,
            raise_on_error=False)
