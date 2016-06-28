from tempfile import mkdtemp
from mocdp.exceptions import mcdp_dev_warning
from contextlib import contextmanager
from mcdp_library.utils.dir_from_package_nam import dir_from_package_name
import os
from mcdp_report.utils import safe_makedirs
from system_cmd.meat import system_cmd_result
from system_cmd.structures import CmdException
from mcdp_library.utils.locate_files_imp import locate_files

__all__ = ['GraphDrawingContext']

STYLE_GREENRED = 'greenred'
STYLE_GREENREDSYM = 'greenredsym'
COLOR_DARKGREEN = 'darkgreen'
COLOR_DARKRED = 'red'

class GraphDrawingContext():
    def __init__(self, gg, parent, yourname, level=0, tmppath=None, style='default',
                 images_paths=[]):
        self.gg = gg
        self.parent = parent
        self.yourname = yourname
        self.level = level

        if tmppath is None:
            tmppath = mkdtemp(suffix="dp-icons")
            mcdp_dev_warning('need to share icons')
            # print('created tmp directory %r' % tmppath)
        self.tmppath = tmppath
        self.images_paths = images_paths

        self.all_nodes = []

        self.set_style(style)

    def get_all_nodes(self):
        return self.all_nodes

    def newItem(self, label):

        n = self.gg.newItem(label, parent=self.parent)
        # print('New item %r sub of %r' % (n['id'], self.parent['id'] if self.parent else '-'))

        self.all_nodes.append(n)
        return n

    def child_context(self, parent, yourname):
        c = GraphDrawingContext(gg=self.gg, parent=parent, yourname=yourname,
                                level=self.level + 1, tmppath=self.tmppath, style=self.style,
                                images_paths=self.images_paths)
        return c

    @contextmanager
    def child_context_yield(self, parent, yourname):
        c = self.child_context(parent=parent, yourname=yourname)
        yield c
        self.all_nodes.extend(c.all_nodes)


    def styleApply(self, sname, n):
        self.gg.styleApply(sname, n)

    def newLink(self, a, b, label=None):
        return self.gg.newLink(a, b, label)

    def styleAppend(self, a, b, c):
        self.gg.styleAppend(a, b, c)

    def set_style(self, style):
        self.style = style
        if style == 'default':
            self.policy_enclose = 'always_except_first'
            self.policy_skip = 'never'
        elif style == 'clean':
            self.policy_enclose = 'only_if_unconnected'
            self.policy_skip = 'if_second_simple'
        elif style in [STYLE_GREENRED, STYLE_GREENREDSYM]:
            self.policy_enclose = 'always_except_first'
            self.policy_skip = 'never'

        else:
            raise ValueError(style)

        if style in [STYLE_GREENRED, STYLE_GREENREDSYM]:
            self.gg.styleAppend('splitter', 'style', 'filled')
            self.gg.styleAppend('splitter', 'shape', 'point')
            self.gg.styleAppend('splitter', 'width', '0.1')
            self.gg.styleAppend('splitter', 'color', 'red')
        else:
            self.gg.styleAppend('splitter', 'style', 'filled')
            self.gg.styleAppend('splitter', 'shape', 'point')
            self.gg.styleAppend('splitter', 'width', '0.1')
            self.gg.styleAppend('splitter', 'color', 'black')

    def should_I_enclose(self, ndp):
        if hasattr(ndp, '_hack_force_enclose'):
            return True

        if self.level == 0:
            return False

        if self.policy_enclose == 'always_except_first':
            return True
        elif self.policy_enclose == 'only_if_unconnected':
            unconnected = not ndp.is_fully_connected()
            if unconnected:
                return True
            else:
                return self.yourname is not None
        else:
            raise ValueError(self.policy_enclose)

    def should_I_skip_leq(self, context, c):
        from mcdp_report.gg_ndp import is_simple
        if self.policy_skip == 'never':
            return False
        elif self.policy_skip == 'if_second_simple':
            second_simple = is_simple(context.names[c.dp2])
            # first_simple = is_simple(context.names[c.dp1])
            # any_simple = second_simple or first_simple
            # both_simple = second_simple and first_simple

            mcdp_dev_warning('Add options here')
            skip = second_simple
            return skip
        else:
            assert False, self.policy_skip

    def get_temp_path(self):
        return self.tmppath

    def _get_default_imagepath(self):
        base = dir_from_package_name('mcdp_report')
        imagepath = os.path.join(base, 'icons')
        if not os.path.exists(imagepath):
            raise ValueError('Icons path does not exist: %r' % imagepath)
        return imagepath

    def get_icon(self, options):
        tmppath = self.get_temp_path()
        # imagepath = self.get_imagepath()
        imagepaths = [self._get_default_imagepath()]
        imagepaths.extend(self.images_paths)
        best = choose_best_icon(options, imagepaths, tmppath)
        return best

    def decorate_arrow_function(self, l1):
        propertyAppend = self.gg.propertyAppend
        if self.style == STYLE_GREENRED:

            propertyAppend(l1, 'color', COLOR_DARKGREEN)
            propertyAppend(l1, 'arrowhead', 'normal')
            propertyAppend(l1, 'arrowtail', 'none')
            propertyAppend(l1, 'dir', 'both')

        if self.style == STYLE_GREENREDSYM:
            propertyAppend(l1, 'color', 'darkgreen')
            propertyAppend(l1, 'arrowhead', 'dot')
            propertyAppend(l1, 'arrowtail', 'none')
            propertyAppend(l1, 'dir', 'both')


    def decorate_arrow_resource(self, l2, split=False):
        propertyAppend = self.gg.propertyAppend

        if self.style == STYLE_GREENRED:
            propertyAppend(l2, 'color', COLOR_DARKRED)
            propertyAppend(l2, 'arrowtail', 'inv')
            propertyAppend(l2, 'arrowhead', 'none')
            propertyAppend(l2, 'dir', 'both')

        if self.style == STYLE_GREENREDSYM:
            propertyAppend(l2, 'color', COLOR_DARKRED)
            propertyAppend(l2, 'arrowtail', 'dot')
            propertyAppend(l2, 'arrowhead', 'none')
            propertyAppend(l2, 'dir', 'both')


    def decorate_resource_name(self, n):
        propertyAppend = self.gg.propertyAppend

        if self.style in  [STYLE_GREENRED, STYLE_GREENREDSYM]:
            propertyAppend(n, 'fontcolor', COLOR_DARKRED)

    def decorate_function_name(self, n):
        propertyAppend = self.gg.propertyAppend
        if self.style in  [STYLE_GREENRED, STYLE_GREENREDSYM]:
            propertyAppend(n, 'fontcolor', COLOR_DARKGREEN)



def choose_best_icon(iconoptions, imagepaths, tmppath):
    # logger.debug('Looking for %s.' % (str(iconoptions)))
    exts = ['png', 'jpg']
    for option in iconoptions:
        if option is None:
            continue
        for imagepath in imagepaths:
            for ext in exts:
                basename = '%s.%s' % (option, ext)
                files = locate_files(imagepath, basename)
                if files:
                    f = files[0]
                    return resize_icon(f, tmppath, 100)
    # logger.debug('Could not find PNG icon for %s.' % (str(iconoptions)))
    return None


def resize_icon(filename, tmppath, size):

    res = os.path.join(tmppath, 'resized', str(size))

    safe_makedirs(res)
    resized = os.path.join(res, os.path.basename(filename))
    if not os.path.exists(resized):
        cmd = ['convert', filename, '-resize', '%s' % size, resized]
        try:
            # print('running graphviz')
            system_cmd_result(cwd='.', cmd=cmd,
                     display_stdout=False,
                     display_stderr=False,
                     raise_on_error=True)
            # print('done')
        except CmdException:
            raise
    return resized

