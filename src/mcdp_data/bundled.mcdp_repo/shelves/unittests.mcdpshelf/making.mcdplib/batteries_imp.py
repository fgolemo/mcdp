# -*- coding: utf-8 -*-
from textwrap import dedent

def save_files(a):
    """ Saves the files in result['files'] """
    files = a.result['files']
    for fn, contents in files.items():
        with open(fn, 'w') as f:
            f.write(contents)

    return "Saved the files %s" % ",".join(list(files))

def instructions(a):
    result = a.result
    bom = result['bom']

    instructions = dedent("""\

    Please buy these: %s

    """ % bom)

    if not 'files' in result:
        result['files'] = {}

    result['files']['instructions.txt'] = instructions

    return  {}


def collect_bom(a):  # @UnusedVariable
    """ Collects the bill of materials from the children. """
    collected = set()
    for v in a.subresult.values():
        if isinstance(v, dict) and 'bom' in v:
            collected.update(v['bom'])
    return collected


def BatterySLA(a):
    return {'bom': ['BatterySLA']}
