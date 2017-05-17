from bs4 import BeautifulSoup
import sys
from mcdp_docs.manual_join_imp import write_split_files, add_prev_next_links,\
    split_in_files, update_refs
from bs4.element import Tag
from mcdp_utils_xml.parsing import bs

disqus = """
<div id='disqus_section'>
<div id="disqus_thread"></div>
<script>

/**
*  RECOMMENDED CONFIGURATION VARIABLES: EDIT AND UNCOMMENT THE SECTION BELOW TO INSERT DYNAMIC VALUES FROM YOUR PLATFORM OR CMS.
*  LEARN WHY DEFINING THESE VARIABLES IS IMPORTANT: https://disqus.com/admin/universalcode/#configuration-variables*/
/*
var disqus_config = function () {
this.page.url = PAGE_URL;  // Replace PAGE_URL with your page's canonical URL variable
this.page.identifier = PAGE_IDENTIFIER; // Replace PAGE_IDENTIFIER with your page's unique identifier variable
};
*/
(function() { // DON'T EDIT BELOW THIS LINE
var d = document, s = d.createElement('script');
s.src = 'https://duckuments.disqus.com/embed.js';
s.setAttribute('data-timestamp', +new Date());
(d.head || d.body).appendChild(s);
})();
</script>
<noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
</div>
"""

def split_file(html, directory):
    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    body = soup.html.body
    # extract the main toc if it is there
    main_toc = body.find(id='main_toc')
#     if main_toc: 
#         main_toc.extract()
        
    assert body is not None, soup
    filename2contents = split_in_files(body)
    add_prev_next_links(filename2contents)
    for filename, contents in list(filename2contents.items()):
        html = Tag(name='html')
        head = soup.html.head.__copy__()
        html.append(head)
        body = Tag(name='body')
        if main_toc:
            tocdiv = Tag(name='div')
            tocdiv.attrs['id'] = 'tocdiv'
            tocdiv.append(main_toc.__copy__())
        body.append(tocdiv)
        body.append(contents)
        html.append(body)
    
        PAGE_IDENTIFIER = filename.replace('.html', '')
        PAGE_URL = 'https://duckietown.github.io/duckuments/master/' + filename
        s = disqus
        s = s.replace('PAGE_IDENTIFIER', PAGE_IDENTIFIER)    
        s = s.replace('PAGE_URL', PAGE_URL)
        disqus_section = bs(s)
        from mcdp import logger
        logger.info(str(s))
        body.append(disqus_section)
        
        filename2contents[filename] = html
    
    update_refs(filename2contents)
    
    write_split_files(filename2contents, directory)

        
if __name__ == '__main__':
    filename = sys.argv[1]
    directory = sys.argv[2]
    html = open(filename).read()
    
    split_file(html, directory)

