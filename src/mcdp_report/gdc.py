# -*- coding: utf-8 -*-
from contextlib import contextmanager
import os
from tempfile import mkdtemp, NamedTemporaryFile

from contracts.utils import check_isinstance, indent
from system_cmd import CmdException, system_cmd_result

from mcdp import MCDPConstants
from mcdp.exceptions import mcdp_dev_warning
from mcdp_utils_misc import dir_from_package_name, get_mcdp_tmp_dir, locate_files, memoize_simple

from .utils import safe_makedirs
from contracts import contract
from mcdp_report.image_source import ImagesSource, ImagesFromPaths, TryMany,\
    NoImageFound
from mcdp_report.gg_utils import check_not_lfs_pointer


__all__ = [
    'GraphDrawingContext',
]

STYLE_GREENRED = 'greenred'
STYLE_GREENREDSYM = 'greenredsym'
COLOR_DARKGREEN = 'darkgreen'
COLOR_DARKRED = '#861109'



class GraphDrawingContext(object):
    @contract(image_source=ImagesSource)
    def __init__(self, gg, parent, yourname, level=0,
                 tmppath=None, style='default',
                 image_source=None, skip_initial=True):
        self.gg = gg
        self.parent = parent
        self.yourname = yourname
        self.level = level
#         self.library = library

        if tmppath is None:
            d = get_mcdp_tmp_dir()
            prefix = 'GraphDrawingContext_tmppath'
            tmppath = mkdtemp(dir=d, prefix=prefix)
            mcdp_dev_warning('need to share icons')

        self.tmppath = tmppath
        self.image_source = image_source

        self.all_nodes = []

        self.set_style(style)
        self.skip_initial = skip_initial

    def child_context(self, parent, yourname):
        c = GraphDrawingContext(gg=self.gg,
                                parent=parent,
#                                 library=self.library,
                                yourname=yourname,
                                level=self.level + 1,
                                tmppath=self.tmppath,
                                style=self.style,
                                image_source=self.image_source,
                                skip_initial=self.skip_initial)
        return c


    def get_all_nodes(self):
        return self.all_nodes

    def newItem(self, label):

        n = self.gg.newItem(label, parent=self.parent)
        # print('New item %r sub of %r' % (n['id'], self.parent['id'] if self.parent else '-'))

        self.all_nodes.append(n)
        return n

  
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
    
    @contract(options='seq(str|None)')
    def get_icon(self, options, raise_if_not_found=False): 
        imagepaths = []
        imagepaths.append(self._get_default_imagepath())

        libraries = os.path.join(dir_from_package_name('mcdp_data'), 'libraries')
        imagepaths.append(os.path.join(libraries, 'FDM.' + MCDPConstants.shelf_extension, 
                                       'fdm.' + MCDPConstants.library_extension))
        imagepaths.append(os.path.join(libraries, 'FDM.' +  MCDPConstants.shelf_extension, 
                                       'mechanisms.' + MCDPConstants.library_extension))
        sources = []
        sources.append(self.image_source)
        sources.append(ImagesFromPaths(imagepaths))
        image_source = TryMany(sources) 

        try:
            best = choose_best_icon(options, image_source)
        except NoImageFound:
            if raise_if_not_found:
                raise 
            return None
        resized = resize_icon(best, MCDPConstants.gdc_image_size_pixels)
        return resized

    def decorate_arrow_function(self, l1):
        propertyAppend = self.gg.propertyAppend

        if self.style == STYLE_GREENRED:
            propertyAppend(l1, 'color', COLOR_DARKGREEN)
            propertyAppend(l1, 'arrowhead', 'normal')
            propertyAppend(l1, 'arrowtail', 'none')
            propertyAppend(l1, 'dir', 'both')

        if self.style == STYLE_GREENREDSYM:
            propertyAppend(l1, 'color', 'darkgreen')
            propertyAppend(l1, 'fontcolor', COLOR_DARKGREEN)
            propertyAppend(l1, 'arrowhead', 'dot')
            propertyAppend(l1, 'arrowtail', 'none')
            propertyAppend(l1, 'dir', 'both')
        

        mcdp_dev_warning('this above has no effect')
        propertyAppend(l1, 'fontcolor', COLOR_DARKGREEN)

    def decorate_arrow_resource(self, l2):
        propertyAppend = self.gg.propertyAppend

        mcdp_dev_warning('this above has no effect')
        propertyAppend(l2, 'fontcolor', COLOR_DARKRED)

        if self.style == STYLE_GREENRED:
            propertyAppend(l2, 'color', COLOR_DARKRED)
            propertyAppend(l2, 'fontcolor', COLOR_DARKRED)
            propertyAppend(l2, 'arrowtail', 'inv')
            propertyAppend(l2, 'arrowhead', 'none')
            propertyAppend(l2, 'dir', 'both')

        if self.style == STYLE_GREENREDSYM:
            propertyAppend(l2, 'color', COLOR_DARKRED)
            propertyAppend(l2, 'arrowtail', 'dot')
            propertyAppend(l2, 'arrowhead', 'none')
            propertyAppend(l2, 'dir', 'both')

        propertyAppend(l2, 'style', 'dashed')
            


    def decorate_resource_name(self, n):
        propertyAppend = self.gg.propertyAppend

        if self.style in  [STYLE_GREENRED, STYLE_GREENREDSYM]:
            propertyAppend(n, 'fontcolor', COLOR_DARKRED)

    def decorate_function_name(self, n):
        propertyAppend = self.gg.propertyAppend
        if self.style in  [STYLE_GREENRED, STYLE_GREENREDSYM]:
            propertyAppend(n, 'fontcolor', COLOR_DARKGREEN)




# reset with: get_images.cache = {}
@memoize_simple
def get_images(dirname, exts=None):
    if exts is None:
        exts = MCDPConstants.exts_for_icons
        
    """ Returns a dict from lowercase basename to realpath """
    
    pattern = ['*.%s' % ext for ext in exts]
    allfiles = {}
    files = locate_files(dirname, pattern, followlinks=True, normalize=False)
    for f in files:
        basename = os.path.basename(f)
        basename = basename.lower()
        allfiles[basename] = f
    return allfiles

@contract(image_source=ImagesSource)
def choose_best_icon(iconoptions, image_source):
    ''' Returns the name of a file, or raise exception KeyError. '''
#     logger.debug('Looking for %s in %s.' % (str(iconoptions), imagepaths))
    exts = MCDPConstants.exts_for_icons
    iconoptions = [_ for _ in iconoptions if _ is not None]
    errors = []
    for option in iconoptions:
        if option is None:
            continue

        for ext in exts:
            try: 
                data = image_source.get_image(option, ext)
            except NoImageFound as e:
                errors.append(e)
            else:
                temp_file = NamedTemporaryFile(suffix='.'+ext,delete=False)
                with open(temp_file.name, 'wb') as f:
                    f.write(data)
                return temp_file.name  
    if len(errors) == 1:
        raise errors[0]
    else:
        msg = 'Could not find any match for options %r' % iconoptions
        for option, e in zip(iconoptions, errors):
            msg += '\n' + indent(str(e), ' %s > ' % option)
        raise NoImageFound(msg)

def resize_icon(filename, size):
    check_isinstance(filename, str)
    contents = open(filename).read()
    check_not_lfs_pointer(filename, contents)
    
    tmppath = get_mcdp_tmp_dir()
    res = os.path.join(tmppath, 'resized', str(size))

    safe_makedirs(res)
    resized = os.path.join(res, os.path.basename(filename))
    if not os.path.exists(resized):
        cmd = ['convert', 
               filename, 
               '-resize', '%s' % size, 
               # remove alpha - otherwise lulu complains
               '-background', 'white',
                '-alpha','remove',
                '-alpha','off', 
               resized]
        try:

            system_cmd_result(cwd='.', cmd=cmd,
                     display_stdout=False,
                     display_stderr=False,
                     raise_on_error=True)

        except CmdException:
            raise
    return resized

