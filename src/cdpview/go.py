from mocdp.dp_report.report import report_dp1
from mocdp.exceptions import DPInternalError, DPSemanticError, DPSyntaxError
from mocdp.lang.syntax import parse_model
from reprep import Report
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import logging
import os
import sys
import time
logger = logging.getLogger(__name__)




def safe_makedirs(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def watch_main():
    filename = sys.argv[1]
    if not '.cdp' in filename:
        raise ValueError(filename)

    path = os.path.dirname(filename)
    if not path: path = '.'
    out = os.path.splitext(filename)[0]
    safe_makedirs(out)
    def go():
        s = open(filename).read()
        try: 
            ndp = parse_model(s)
        except (DPSyntaxError, DPSemanticError) as e:
            r = Report()
            r.text('error', str(e))

            logger.error("Error while reading %r." % filename)
            logger.error(str(e))
        except DPInternalError as e:
            r = Report()
            r.text('developer_error', str(e))

            logger.error("Developer error while reading %r." % filename)
            logger.error(str(e))
            logger.error("Please file a bug report and attach %r." % filename)
        else:
            logger.info("OK %r" % filename)
            dp = ndp.get_dp()
            r = report_dp1(dp)

        r.to_html(os.path.join(out, 'report_dp1.html'))

    go()
    watch(path, go)
    
    
def watch(path, handler):
    
    class MyWatcher(FileSystemEventHandler):
        def on_modified(self, event):  # @UnusedVariable
            src_path = event.src_path
            if '.cdp' in src_path:
                handler.__call__()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    event_handler = MyWatcher()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    watch_main()
