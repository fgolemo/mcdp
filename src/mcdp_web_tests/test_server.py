from contracts.enabling import all_disabled
from contracts.utils import raise_desc
from multiprocessing.process import Process
from urllib2 import HTTPError
import json
import os
import random
import subprocess
import tempfile
import time
import urllib2

def test_mcdpweb_server(dirname):
    port = random.randint(11000, 15000)
    base = 'http://127.0.0.1:%s' % port

    p = Process(target=start_server, args=(dirname, port,))
    p.start()

    print('sleeping')
    time.sleep(5)

    try:
        url_wrong = base + '/not-existing'
        urllib2.urlopen(url_wrong).read()
    except HTTPError:
        pass
    else:
        raise Exception('Expected 404')

    # now run the spider
    tmpdir = tempfile.mkdtemp(prefix='wget-output')
    cwd = '.'
    cmd = ['wget', '-nv', '-P', tmpdir, '-m', base]
#     res = system_cmd_result(
#             cwd, cmd,
#             display_stdout=True,
#             display_stderr=True,
#             raise_on_error=True)
    sub = subprocess.Popen(
                cmd,
                bufsize=0,
                cwd=cwd)
    sub.wait()

    exc = get_exceptions(port)

    if len(exc) == 0:
        msg = 'Expected at least a not-found error'
        raise Exception(msg)

    if not 'not-existing' in exc[0]:
        raise Exception('Could not find 404 error')

    exc = exc[1:]

    if exc:
        msg = 'Execution raised errors:\n\n'
        msg += str("\n---\n".join(exc))
        raise_desc(Exception, msg)

    url_exit = base + '/exit'
    urllib2.urlopen(url_exit).read()

    print('waiting for start_server() process to exit...')
    p.join()
    print('...clean exit')

def start_server(dirname, port):
    cwd = '.'
    cmd = ['mcdp-web', '-d', dirname, '--port', str(port), '--delete_cache']
    print('starting server')

    env = dict(os.environ)
    if all_disabled():
        env['DISABLE_CONTRACTS'] = "1"

    sub = subprocess.Popen(
                cmd,
                bufsize=0,
                cwd=cwd,
                env=env)
    sub.wait()
    print('mcdp-web exited cleanly')

#     res = system_cmd_result(
#             cwd, cmd,
#             display_stdout=True,
#             display_stderr=True,
#             raise_on_error=True)



def get_exceptions(port):
    base = 'http://127.0.0.1:%s' % port
    url_exit = base + '/exceptions'
    data = urllib2.urlopen(url_exit).read()
    data = str(data)
    s = json.loads(data)
    return s['exceptions']
