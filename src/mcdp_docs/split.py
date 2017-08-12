from mcdp_utils_xml import bs
import sys

from bs4 import BeautifulSoup
from bs4.element import Tag

from .manual_join_imp import write_split_files, add_prev_next_links,\
    split_in_files, update_refs


disqus = """
<style>
#disqus_section {
margin-top: 1em;
}
</style>
<div id='disqus_section'>
    <details>
        <summary>
            Comments (<span class="disqus-comment-count" data-disqus-url="PAGE_URL"></span>)
        </summary>    
        <div id="disqus_thread"></div>
    </details>
</div>

<script>
    var disqus_config = function () {
        this.page.url = "PAGE_URL";  
        this.page.identifier = "PAGE_IDENTIFIER"; 
    };

    (function() { 
        var d = document, s = d.createElement('script');
        s.src = 'https://DISQUS_DOMAIN/embed.js';
        s.setAttribute('data-timestamp', +new Date());
        (d.head || d.body).appendChild(s);
    })();
</script>
<script id="dsq-count-scr" src="https://DISQUS_DOMAIN/count.js" async></script>

"""

def split_file(html, directory):
    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    body = soup.html.body
    # extract the main toc if it is there
    main_toc = body.find(id='main_toc')
    p = bs('<p><a href="index.html">Home</a></p>')
    main_toc.insert(0, p.p)
        
    assert body is not None, soup
    filename2contents = split_in_files(body)
    filename2contents = add_prev_next_links(filename2contents)
    for filename, contents in list(filename2contents.items()):
        html = Tag(name='html')
        head = soup.html.head.__copy__()
        html.append(head)
        body = Tag(name='body')
        if main_toc:
            tocdiv = Tag(name='div')
            tocdiv.attrs['id'] = 'tocdiv'
            toc = main_toc.__copy__()
            del toc.attrs['id']
            tocdiv.append(toc)
        body.append(tocdiv)
        not_toc = Tag(name='div')
        not_toc.attrs['id'] = 'not-toc'
        not_toc.append(contents)
        body.append(not_toc)
        html.append(body)
    
        # append discus section
        PAGE_IDENTIFIER = filename.replace('.html', '')
        PAGE_URL = 'https://duckietown.github.io/duckuments/master/' + filename
        DISQUS_DOMAIN = 'duckuments.disqus.com'
        s = disqus
        s = s.replace('PAGE_IDENTIFIER', PAGE_IDENTIFIER)    
        s = s.replace('PAGE_URL', PAGE_URL)
        s = s.replace('DISQUS_DOMAIN', DISQUS_DOMAIN)
        disqus_section = bs(s)
        disqus_section.name = 'div'
        not_toc.append(disqus_section)
        banner_string = """
<style type="text/css">
#banner {
    display: block;
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
    padding-top: 0.5em;
    padding-left:2em;
    padding-right: 0.5em;
    font-weight: bold !important;
    font-size: 120%;
    //background-color: yellow;
    color: red;
    font-weight: bold;
    padding-bottom: 0.5em;
}
div.super { margin-top: 2em; }
</style>
<div id='banner'>
We are preparing things for Fall 2017. Please pardon our dust as we prepare the Duckiebook.
</div>
"""
        banner = bs(banner_string)
        banner.name = 'div'
        body.insert(0, banner)
        
        filename2contents[filename] = html
    
    update_refs(filename2contents)
#     update_tocdiv_refs(filename2contents)
    
    write_split_files(filename2contents, directory)

# def update_tocdiv_refs(filename2contents):
#     """ Looks for the A elements inside #tocdiv. If they a to
        
        
if __name__ == '__main__':
    filename = sys.argv[1]
    directory = sys.argv[2]
    html = open(filename).read()
    
    split_file(html, directory)

