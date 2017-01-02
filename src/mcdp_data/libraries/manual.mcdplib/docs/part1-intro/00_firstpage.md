
<h1 id='booktitle' nonumber notoc style='margin-top: -3em'>
    <!-- PyMCDP user manual -->
    <!-- The MCDPL co-design modeling language
    and its interactive co-design environment -->
    <!-- A Practical Approach to Co-Design -->
    <!-- Practical Tools for Co-Design -->
    <!-- Formal Tools for Systems Co-Design -->
    <span style='color:white;'>@@{PYMCDP_COMPILE_TIME}</span>
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

<pre id='build_stats'>
    Compiled: @@{PYMCDP_COMPILE_TIME} at @@{PYMCDP_COMPILE_DATE}
    Version @@{PYMCDP_VERSION}.
    <!-- Manual compiled from branch COMPILE_BRANCH on COMPILE_DATE. -->
</pre>

<div id='affiliation'> The author is with the Laboratory of Information and
    Decision Systems at the Massachusetts Institute of Technology; with ETH Zurich;
    with nuTonomy, inc.; and with Duckietown Engineering.
</div>

<h1 notoc nonumber id='toc-heading'>Table of contents</h1>

<!-- place toc here -->
<div id='toc'></div>

<!-- <h2 id='symbols-heading'>Table of important symbols</h2> -->


Media info:

    @page {
    size: 6in 9in;
    margin-top: 1.7cm;
    /*here*/
    margin-bottom: 0.312in;
    @center {
    border: solid 1px black;
    }
    }
    @page :left {
    margin-left: 1cm;
    margin-right: 2cm;
    }
    @page :right {
    margin-left: 2cm;
    margin-right: 1cm;
    }

    Render params: @@{RENDER_PARAMS}


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
