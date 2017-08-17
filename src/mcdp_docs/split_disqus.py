from mcdp_utils_xml import bs



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
def append_disqus(filename, html):
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
    not_toc= html.find(id='not-toc')
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
    html.body.insert(0, banner)
    