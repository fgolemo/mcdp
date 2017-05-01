# -*- coding: utf-8 -*-
from comptests.registrar import run_module_tests, comptest
from mcdp_utils_xml.parsing import bs
from mcdp_docs.tocs import generate_toc
from contracts.utils import indent

@comptest
def test_toc():
    s = """
<html>
<head></head>
<body>
<h1 id='one'>One</h1>

<p>a</p>

<h2 id='two'>Two</h2>

<p>a</p>

<h3 id='three'>Three</h3>

<h2 id='four'>Four</h2>

<p>a</p>
</body>
</html>
    """
    soup = bs(s)
    print soup
#     body = soup.find('body')
    toc = generate_toc(soup)
    s = str(soup)
    expected = ['sec:one', 'sub:two']
    print indent(s, 'transformed > ')
    for e in expected:
        assert e in s
    



if __name__ == '__main__':
    run_module_tests()