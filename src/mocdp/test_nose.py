import sys
from comptests.comptests import main_comptests


def test_nose():
    mydir = 'out-comptests-nose'

    sys.argv = [sys.argv[0],
                 '-o', mydir,
                 '--nonose', 'mocdp', ]
    try:
        main_comptests()
    except SystemExit as e:
        if e.code != 0:
            raise e
