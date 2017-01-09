
<h1 id='booktitle' nonumber notoc style='margin-top: -3em'>
    <!-- PyMCDP user manual -->
    <!-- The MCDPL co-design modeling language
    and its interactive co-design environment -->
    <!-- A Practical Approach to Co-Design -->
    <!-- Practical Tools for Co-Design -->
    <!-- Formal Tools for Systems Co-Design -->
    <span style='color:white;'>@@{PYMCDP_COMPILE_DATE} @@{PYMCDP_COMPILE_TIME} </span>
    <br/>Formal Tools <br/>for <f>Co</f>-<r>Design</r>
</h1>

<div id='author'>
    <p>Andrea Censi</p>
    <!-- <p><a href="http://censi.mit.edu">Andrea Censi</a>

    </p> -->
</div>

<p id='logop'>
    <img src='logo.png'/>
</p>

<div class='abstract'>
</div>



<div id='affiliation'> The author is with the Laboratory of Information and
    Decision Systems at the Massachusetts Institute of Technology; with ETH Zurich;
    with nuTonomy, inc.; and with Duckietown Engineering.
</div>


<div style='page-break-before: always'>
</div>


<h4 nonumber>Alternative versions for this book</h4>

This book is available in several versions:

<ul>
    <li id='version-v_manual_blurb'>
        In print, either hardcover version or softcover version.
    </li>
    <li id='version-v_manual_ipad'>
        PDF, optimized for screen readers.
    </li>
    <li id='version-v_manual_screen'>
        HTML, for viewing on a computers. Includes links to
        interactive demonstrations (diagrams can be edited in PyMCDPWeb).
    </li>
</ul>




<!-- ## License information
The code is available under the GPL license. -->


<img id='license' src="by-nc-sa.svg" style='width: 10em'/>
The book is available under the Creative Commons Attribution NonCommercial ShareAlike
(CC BY-NC-SA) license.

<style type='text/css'>
#license {
    float: right;
    margin-left: 2em;
}
    blockquote#firstquote  p:first-child,
    blockquote#secondquote p:first-child {
        font-style: italic;
    }
    blockquote#firstquote p:not(:first-child) {
        font-size: smaller;
    }
</style>


    Render params: @@{RENDER_PARAMS}
    Compiled: @@{PYMCDP_COMPILE_TIME} at @@{PYMCDP_COMPILE_DATE}
    PyMCDP version @@{PYMCDP_VERSION}.
    <!-- Manual compiled from branch COMPILE_BRANCH on COMPILE_DATE. -->


<h1 notoc nonumber id='toc-heading'>Table of contents</h1>

<!-- place toc here -->
<div id='toc'></div>

<!-- <h2 id='symbols-heading'>Table of important symbols</h2> -->





<style>
    #booktitle, #author {
        font-family: Cambria;
    }
    #booktitle {
        text-align: center; font-size: 45pt !important;
        margin-top: 1em !important;
    }
    #author {
        text-align: center;
        margin-top: 5em;

         a {
        text-decoration: none;
        color: darkblue;
        font-size: 14pt;
        }
    }

    #author, #affiliation {
        color: white;
        margin: 0; padding: 0;
        margin-top: -2em;

    }
    @media print {
        #affiliation {
            float: footnote;
            font-size: smaller;
            text-align: justify;
        }
        #affiliation::footnote-call { display: none;  content: none; }
        #affiliation::footnote-marker { display: none; content: none;  }
    }
    @media screen {
        #affiliation {
            text-align: justify;
            font-size: smaller;
            margin-top: 6em;
        }
    }
    #build_stats {
        margin-top: 4em;
        font-size: smaller;
        font-style: italic;
    }
    #booktitle {
        font-size: 20pt;
        margin-top: 3em;
        font-family: "Berkshire", serif;
    }
    #toc-heading {
        page-break-before: always;
    }
    /*#symbols-heading {
        page-break-before: always;
    }*/
    .abstract {
        padding-left: 3em;
        padding-right: 3em;
    }
    #logop {
        text-align: center;
    }
    #logop  img {
        width: 40%;

        margin-top: 5em;
        margin-bottom: 5em;
    }

    ul.toc { font-size: smaller; }
    ul.toc, ul.toc ul { list-style-type: none; }

</style>
