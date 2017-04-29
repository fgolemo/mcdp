# Some notes about exceptions

Exceptions should have a *trace*.

A *trace* can be None.

A *trace* is a list of <error message>, <suggestion>, and *where*.

A *frame* contains a *where* and a *location*.

A *where* has a "filename", which can be:
- a filename (starts with "/")
- an hdb:// path:

    hdb://repos/<repo-name>/shelves/<shelf_name>/versions/<version>/libraries/<ibrary>/things/<spec-name>/<spec>/

From the hdb:// url we can:
1) link to the filename (assuming we know the disk map)
2) link to a webpage
