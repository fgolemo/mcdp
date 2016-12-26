
<h1 id='booktitle' nonumber>
    <!-- PyMCDP user manual -->
    <!-- The MCDPL co-design modeling language <br/>
    and its interactive co-design environment -->
    <!-- A Practical Approach to Co-Design -->
    <!-- Practical Tools <br/>for Co-Design -->
    <!-- Formal Tools <br/>for Systems Co-Design -->
    Formal Tools <br/>for <f>Co</f>-<r>Design</r>
</h1>

<div id='author'>
    <p><a href="http://censi.mit.edu">Andrea Censi</a>

    </p>

</div>

<p id='logop'>
    <img src='logo.png'/>
</p>

<div class='abstract'>
    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
    proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
</div>
<!--
<div id='build_stats'>
    Version PYMCDP_VERSION. Manual compiled from branch COMPILE_BRANCH on COMPILE_DATE.
</div> -->

<div id='affiliation'>
    The author is with the Laboratory of Information and Decision Systems at the Massachusetts Institute of Technology;
    with ETH Zurich; with nuTonomy, inc.; and with Duckietown Engineering.
</div>

<h2 nonumber id='toc-heading'>Table of contents</h2>

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
    
    #author, #affiliation { display: none; }
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
