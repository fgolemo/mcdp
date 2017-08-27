from mcdp_utils_xml import bs

def add_footnote_polyfill(soup):
    body = soup.find('body')
    if body is None:
        raise ValueError(str(soup))
    x = bs(footnote_javascript)
    body.append(x)
    
footnote_javascript_old = r'''
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

function click_marker(that_id) {
    // e = e || window.event;
    // var src = e.target || e.srcElement;

    console.log('click ' + that_id);
    panel = document.getElementById(that_id);
    current = panel.style.display;
    if (current == 'block') {
        panel.style.display = 'none';
    } else {
        panel.style.display = 'block';
    }
}

if(prince==null) {
    // Do one at a time
    var i = 0;
    while(true) {
        i+= 1;
        var elements = document.getElementsByTagName('footnote');
        console.log('Found footnotes: ' + elements.length);
        if(elements.length == 0) {
            break;
        }
    // for (var i=0; i<elements.length; i++) {
        var e = elements[0];
        var d = document.createElement('div');
        d.innerHTML = e.innerHTML;
        d.classList.add('footnote-simulation');
        this_id = 'myfootnote' + i;
        d.id = this_id;

        var a = document.createElement('a');
        a.classList.add('footnote-marker');
        a.innerHTML = '&dagger;';
        a.href = "javascript:click_marker('" + this_id + "')";
        // a.onclick = click_marker;

        // function(this) {
        //     console.log('click ' + this.id);
        //     current = d.style.display;
        //     if (current == 'block') {
        //         d.style.display = 'none';
        //     } else {
        //         d.style.display = 'block';
        //     }
        // }
        e.parentNode.insertBefore(a, e);
        e.parentNode.insertBefore(d, e);
        e.parentNode.removeChild(e);
    }
}
</script>
'''