import numpy as np
import getpass

__all__ = ['MCDPConstants']


class MCDPConstants(object):
    """ Some system-wide constants """
    
    # source
    
    # preferred indent
    indent = 4
    # number of spaces to which a tab is equivalent
    tabsize = 4 
        
    
    #
    # Compilation stage
    #
    
    # only compile to graphs using two-factor multiplication for functions
    force_mult_two_functions = True
    # only compile to graphs using two-factor multiplication for resources
    force_mult_two_resources = True
    
    force_plus_two_resources = True
    
    # force_plus_two_functions = True # currently unused (InvPlus2 -> InvPlusN)
    
    # TODO: make algo configurable for invplus, etc. see also: InvMult2.ARGO 
    
    #
    # Testing
    #
    
    Nat_chain_include_maxint = False
    Rcomp_chain_include_tiny = False
    Rcomp_chain_include_eps = False
    Rcomp_chain_include_max = False
    
    # test the correspondence between h and h* (currently failing)
    test_dual01_chain = False
    
    # Ignore graphviz errors in unit tests
    test_ignore_graphviz_errors = True
    
    # Ignore the known failures
    test_include_primitivedps_knownfailures = False
    
    # only draw 1/20th of pictures
    test_fraction_of_allreports = 0.025
     
    test_insist_correct_html_from_ast_to_html = False
    #
    # UI
    #
    
    # Affects things like Nat
    use_unicode_symbols = True
#     if not use_unicode_symbols:
#         msg =( 'Note that use_unicode_symbols is false, which is not suitable for printing')
#         warnings.warn(msg)

    # Any time we need to solve a relation like (r1*r2==f),
    # we will bound r1 and r2 in the interval [eps, 1/eps].
    inv_relations_eps = np.finfo(float).eps # ~1e-16
    # TODO: think whether this makes us optimistic or pessimistic, and where
    
    # threshold above which we output a warning
    parsing_too_slow_threshold = 0.5

    log_cache_writes = False
    
    InvPlus2Nat_max_antichain_size=  100000
    InvMult2Nat_memory_limit   = 10000
    
    # Actually write to disk the reports
    test_allformats_report_write = False
    
    # this can be changed by customer. The other configuration switches
    # are all relative.
    diagrams_fontsize = 14

    diagrams_smallimagesize_rel = 0.4
    diagrams_leqimagesize_rel = 0.3
    diagrams_bigimagesize_rel = 60  
    
    # how much to scale the produced svg from dots
    # if diagrams_fontsize = 14 and you want the font to be 10,
    # use 10.0
    svg_apparent_fontsize = 10.0 
    scale_svg = svg_apparent_fontsize / float(diagrams_fontsize)
    
    # useful for debugging css
    # for (1) manual and (2) mcdp-render
    manual_link_css_instead_of_including = True
    
    
#     pdf_to_png_dpi = 300 # dots per inch
    pdf_to_png_dpi = 100 # dots per inch
    
    docs_xml_allow_empty_attributes = ['np', 'noprettify', 'nonumber', 'notoc',
                                        'mcdp-value', 'mcdp-poset']

    # directories ignored by locate_files
    locate_files_ignore_patterns = ['node_modules', '.git', 'commons', '_cached', 
                                    '_mcdpweb_cache', 'resized', 
                                    '1301-jbds-figures', 'out', 'out-html', 'reprep-static',
                                    '*.html_resources', 'out-*', 'compmake', '*.key']

    # images used to look for icons for DPs 
    exts_for_icons = ('png', 'jpg', 'PNG', 'JPG') # 'jpeg', 'JPEG') # XXX
#     exts_for_icons = ('png', 'jpg', 'PNG', 'JPG', 'jpeg', 'JPEG') # XXX
    # all images 
    exts_images = exts_for_icons + ('svg', 'SVG', 'pdf', 'PDF')
    
    ENV_TEST_LIBRARIES = 'MCDP_TEST_LIBRARIES'
    ENV_TEST_LIBRARIES_EXCLUDE = 'MCDP_TEST_LIBRARIES_EXCLUDE'
    ENV_TEST_SKIP_MCDPOPT = 'MCDP_TEST_SKIP_MCDPOPT'
    
    
    
    # deprecated, used as attr for implementation spaces
    ATTRIBUTE_NDP_RECURSIVE_NAME = 'ndp_recursive_name'
    
    # added to NamedDPs
    ATTRIBUTE_NDP_MAKE_FUNCTION = 'make'
    
    # added 
    ATTR_LOAD_NAME = '__mcdplibrary_load_name'
    ATTR_LOAD_LIBNAME = '__mcdplibrary_load_libname'
    ATTR_LOAD_REALPATH = '__mcdplibrary_load_realpath'
    
    log_duplicates = False

        
    ext_ndps = 'mcdp'
    ext_posets = 'mcdp_poset'
    ext_values = 'mcdp_value'
    ext_templates = 'mcdp_template'
    ext_primitivedps = 'mcdp_primitivedp'
    ext_doc_md = 'md'  # library document
    
    ext_explanation1 = 'expl1.md'  # before the model
    ext_explanation2 = 'expl2.md'  # after the model
    
    shelf_extension = 'mcdpshelf'
    shelf_desc_file = 'mcdpshelf.yaml'
    
    user_extension = 'mcdp_user'
    user_desc_file = 'user.yaml'
    user_image_file = 'user.jpg'
    library_extension = 'mcdplib'
    
    all_extensions = (ext_ndps, ext_posets, ext_values, ext_templates, ext_primitivedps,
                      ext_explanation1, ext_explanation2, ext_doc_md) + exts_images

    repo_prefix = 'mcdpr:'
    
    gdc_image_size_pixels = 150

    # if True, disables computing the actual images.
    test_spider_exclude_images = True
    
    
    class Privileges:
        DISCOVER = 'discover'
        SUBSCRIBE = 'subscribe' # = can change the subscription status
        READ = 'read'
        WRITE = 'write'
        ADMIN = 'admin'
        ACCESS = 'access'
        SPECIAL_ALL_WILDCARD = 'all'
        VIEW_USER_LIST = 'view_user_list'

        # Remember to change somewhere else
        # view the public profile
        VIEW_USER_PROFILE_PUBLIC = 'view_user_profile_public'
        # view the private profile (email)
        VIEW_USER_PROFILE_PRIVATE = 'view_user_profile_private'
        # view the internal details profile (ids of connected accounts, etc.)
        VIEW_USER_PROFILE_INTERNAL = 'view_user_profile_internal'
        EDIT_USER_PROFILE = 'edit_user_profile'
        
        IMPERSONATE_USER = 'impersonate'
        
        ALL_PRIVILEGES = [DISCOVER, SUBSCRIBE, READ, WRITE, ADMIN, ACCESS, SPECIAL_ALL_WILDCARD, 
               VIEW_USER_LIST, VIEW_USER_PROFILE_PUBLIC, VIEW_USER_PROFILE_PRIVATE,
               VIEW_USER_PROFILE_INTERNAL, EDIT_USER_PROFILE, IMPERSONATE_USER]
        
    USER_ANONYMOUS = 'anonymous'
    # todo: change this to system.Authenticated
    # todo: change this to system.Everyone
    AUTHENTICATED = 'Authenticated'
    EVERYONE = 'Everyone' 
    ALLOW = 'Allow'
    DENY = 'Deny' 
    # This is somebody who is granted all permissions
    ROOT = 'system:root'
    
    default_acl = [
        [ALLOW, EVERYONE, Privileges.DISCOVER],
        # we don't want to allow anonymous to desubscribe
        #['Allow', 'Everyone', 'subscribe'],
        [ALLOW, EVERYONE, Privileges.READ],
        [ALLOW, EVERYONE, Privileges.WRITE],
        [ALLOW, EVERYONE, Privileges.ADMIN],
    ]
    
    allow_soft_matching = True
    
    softy_mode = True
    
    