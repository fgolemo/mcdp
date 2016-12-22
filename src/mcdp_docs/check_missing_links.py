from mocdp import logger


def check_if_any_href_is_invalid(html):
    from mcdp_web.renderdoc.xmlutils import bs
    errors = []
    math_errors = []
    soup = bs(html) 
    for a in soup.select('a[href^="#"]'):
        href = a['href']
        if a.has_attr('class') and  "mjx-svg-href" in a['class']:
            msg = 'Invalid math reference: %s' % str(a)
            msg = 'Invalid math reference (sorry, no details).'
            logger.error(msg)
            math_errors.append(msg)
            continue 
#         if href == "#": continue
        assert href.startswith('#')
        sel = href 
        selection = list(soup.select(sel))
        if not selection:
            msg = 'No element found matching %s' % str(a)
            logger.error(msg)
            errors.append(msg)
            continue
        if len(selection) > 1:
            msg = 'More than one element matching %r.' % href
            logger.error(msg)
            errors.append(msg)
            continue
    return errors, math_errors