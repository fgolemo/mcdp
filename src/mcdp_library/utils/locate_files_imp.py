from collections import defaultdict
from contracts import contract
import fnmatch
import os

__all__ = [
    'locate_files',
]


@contract(returns='list(str)', directory='str',
          pattern='str', followlinks='bool')
def locate_files(directory, pattern, followlinks=True,
                 include_directories=False,
                 include_files=True,
                 normalize=True):
    # print('locate_files %r %r' % (directory, pattern))
    filenames = []

    for root, dirnames, files in os.walk(directory, followlinks=followlinks):
        if include_files:
            for f in files:
                if fnmatch.fnmatch(f, pattern):
                    filename = os.path.join(root, f)
                    filenames.append(filename)

        if include_directories:
            for d in dirnames:
                if fnmatch.fnmatch(d, pattern):
                    filename = os.path.join(root, d)
                    filenames.append(filename)

    if normalize:
        real2norm = defaultdict(lambda: [])
        for norm in filenames:
            real = os.path.realpath(norm)
            real2norm[real].append(norm)
            # print('%s -> %s' % (real, norm))

    #     for k, v in real2norm.items():
    #         if len(v) > 1:
    #             msg = 'In directory:\n\t%s\n' % directory
    #             msg += 'I found %d paths that refer to the same file:\n'
    #             for n in v:
    #                 msg += '\t%s\n' % n
    #             msg += 'refer to the same file:\n\t%s\n' % k
    #             msg += 'I will silently eliminate redundancies.'
    #             logger.warning(v)

        return list(real2norm.keys())
    else:
        return filenames
