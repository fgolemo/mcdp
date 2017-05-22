from mcdp_utils_xml.parsing import bs

def add_footnote_polyfill(soup):
    body = soup.find('body')
    x = bs(footnote_javascript)
    body.append(x)
    
footnote_javascript = r'''
<style>
.footnote-simulation {
    font-size: smaller;
    padding-left: 2em;
    border-left: solid 2px grey;
    /*position: absolute;
    right: -20em;
    width: 20em;*/
    background-color: white;
    padding: 4px;

    display: none;
}
.footnote-marker {
    margin-left: 2px;
    color: blue !important;
    text-decoration: underline !important;
}
</style>
<script>
try {
    prince = Prince;
} catch (e) {
    console.log("Not running in Prince");
    prince = null;
}
if(prince==null) {
    var elements = document.getElementsByTagName('footnote');
    for (var i=0; i<elements.length; i++) {
        e = elements[i];
        var d = document.createElement('div');
        d.innerHTML = e.innerHTML;
        d.classList.add('footnote-simulation');

        var a = document.createElement('a');
        a.classList.add('footnote-marker');
        a.innerHTML = '&dagger;';
        a.href = "javascript:";
        a.onclick=function(){
            // console.log('click');
            current = d.style.display;
            if (current == 'block') {
                d.style.display = 'none';
            } else {
                d.style.display = 'block';
            }
        }
        e.parentNode.insertBefore( a, e);
        e.parentNode.insertBefore( d, e);
        e.parentNode.removeChild(e);
    }
}
</script>

'''