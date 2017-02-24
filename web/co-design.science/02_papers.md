---
layout: page
title: Papers & slides
permalink: /papers/
---

<style type='text/css'>
    img.slides-keynote{
        border:0; margin-bottom:-3px; height: 17px;
    }
    img.slides-ppt {
        border:0; margin-bottom:-3px; height: 17px;
    }
    img.slides-pdf {
        border:0; margin-bottom:-3px; height: 17px;
    }
    div.cover {
        float: left;
        clear: left;
        display: block; 
        margin-right: 2em; 
        padding-right: 1em;
        margin-bottom: 3em;
    }
    div.cover img, div.cover iframe {
        width: 20em; 
        border: solid 1px #888888;
        box-shadow: 2px 2px 5px #888888;
    }
    div.cover iframe { height: 15em;}
    div.talk { 
        /<em>border: solid 1px black;</em>/
        padding: 0; margin: 0;
        float: left; display: block;
        width: 25em;
        margin-right: -10em;
    }
    div.talk ul {margin-top: 1em;}
</style> 

<div class='cover'>
    <img class='cover' 
         src='http://purl.org/censi/research/2015-robotics-seminar/1511-censi-robotics-seminar.png'/>
</div>

<div class='talk'>
    <strong>&ldquo;Monotone Co-Design Problems: or, everything is the same&rdquo;</strong>.

    <ul>
        <li>
            <img class="slides-pdf" src='/media/pdf.gif'/>
            <a href="http://purl.org/censi/research/2015-robotics-seminar/1511-censi-robotics-seminar-steps.pdf">PDF</a></li>

        <li>
            <img class="slides-keynote" src='/media/keynote.gif'/>
            <a href="http://purl.org/censi/research/2015-robotics-seminar/1511-censi-robotics-seminar.key">Keynote</a>
        </li>
        <li>
             <img class="slides-ppt" src='/media/slides-ppt.gif'/>
             <a href="http://purl.org/censi/research/2015-robotics-seminar/1511-censi-robotics-seminar.pptx">Powerpoint (automatically converted)</a>

        </li>
        
    </ul>
</div>

<div style='clear:both'/>

<!--
	Just copy the code from publications below

	Might want to substitute 
	http://purl.org/censi/web/media/paper-icons
	http://censi.mit.edu/media/paper-icons

-->

This paper is currently the best reference:


<div class='pub-ref-desc'>
    <img class='icon' src='https://censi.science/media/paper-icons/censi16codesign.png'/>
    <p class='pub-ref-short'><span class="author"><span class="author-ac">Andrea Censi</span>.</span>
    <span class="title">A mathematical theory of co-design.</span>
    Technical Report, Laboratory for Information and Decision Systems, MIT, September 2016.
    <span class="links"><span class="pdf"><a href="https://arxiv.org/pdf/1512.08055"><img style='border:0; margin-bottom:-6px'  src='/media/pdf.gif'/> pdf</a></span><span class="url"><a href="https://arxiv.org/abs/1512.08055"><img style='border:0; margin-bottom:-6px; height: 17px'  src='/media/web.gif'/> supp. material</a></span></span><a class='pub-ref-bibtex-link' onclick='javascript:$("#censi16codesign").toggle();' href='javascript:void(0)'>bibtex</a><pre class='pub-ref-bibtex' id='censi16codesign' style='display: none;'>@techreport{censi16codesign,
        author = "Censi, Andrea",
        title = "A Mathematical Theory of Co-Design",
        url = "https://arxiv.org/abs/1512.08055",
        month = "September",
        year = "2016",
        pdf = "https://arxiv.org/pdf/1512.08055",
        institution = "Laboratory for Information and Decision Systems, MIT"
    }</pre></p>
    <div class='desc'>
        <p>This paper introduces a theory of co-design that describes "design problems", defined as tuples of "functionality space", "implementation space", and "resources space", together with a feasibility relation that relates the three spaces. Design problems can be interconnected together to create "co-design problems", which describe possibly recursive co-design constraints among subsystems.</p>
        <p class='read-more'><a href='https://arxiv.org/abs/1512.08055'>read more...</a></p>
    </div><div style='clear:both'></div>
</div>

This is a rather technical paper with more examples and the description of the certainty handling mechanism currently implemented:

<div class='pub-ref-desc'>
    <img class='icon' src='https://censi.science/media/paper-icons/censi17uncertainty.png'/>
    <p class='pub-ref-short'><span class="author"><span class="author-ac">Andrea Censi</span>.</span>
    <span class="title">Uncertainty in monotone co-design problems.</span>
    <em>Robotics and Automation Letters</em>, 2017.
    <span class="links"><span class="pdf"><a href="https://arxiv.org/pdf/1609.03103"><img style='border:0; margin-bottom:-6px'  src='/media/pdf.gif'/> pdf</a></span><span class="url"><a href="https://arxiv.org/abs/1609.03103"><img style='border:0; margin-bottom:-6px; height: 17px'  src='/media/web.gif'/> supp. material</a></span></span><a class='pub-ref-bibtex-link' onclick='javascript:$("#censi17uncertainty").toggle();' href='javascript:void(0)'>bibtex</a><pre class='pub-ref-bibtex' id='censi17uncertainty' style='display: none;'>@article{censi17uncertainty,
        author = "Censi, Andrea",
        title = "Uncertainty in Monotone Co-Design Problems",
        url = "https://arxiv.org/abs/1609.03103",
        journal = "Robotics and Automation Letters",
        year = "2017",
        pdf = "https://arxiv.org/pdf/1609.03103",
        institution = "Laboratory for Information and Decision Systems, MIT"
    }</pre></p>
    <div class='desc'>
        <p>This paper concerns the introduction of uncertainty in the MCDP framework. Uncertainty has two roles: first, it allows to deal with limited knowledge in the models; second, it also can be used to generate consistent relaxations of a problem, as the computation requirements can be lowered should the user accept some uncertainty in the answer.</p>
        <p class='read-more'><a href='https://arxiv.org/abs/1609.03103'>read more...</a></p>
    </div><div style='clear:both'></div>
</div>





<!--

This is an application to computation/resources graphs:

<div class='pub-ref-desc'>
    <img class='icon' src='http://censi.mit.edu/media/paper-icons/censi15rara.png'/>
    <p class='pub-ref-short'><span class="author">A.C..</span>
    <span class="title">Synthesis of resource-aware robotic applications.</span>
    Technical Report, Laboratory for Information and Decision Systems/MIT, October 2015.
    <span class="links"><span class="pdf"><a href="http://purl.org/censi/research/201510-monotone/3-ResourceAwareRoboticApplications.pdf"><img style='border:0; margin-bottom:-6px'  src='/media/pdf.gif'/> pdf</a></span></span><a class='pub-ref-bibtex-link' onclick='javascript:$("#censi15rara").toggle();' href='javascript:void(0)'>bibtex</a><pre class='pub-ref-bibtex' id='censi15rara' style='display: none;'>@techreport{censi15rara,
        author = "Censi, Andrea",
        title = "Synthesis of resource-aware robotic applications",
        month = "October",
        year = "2015",
        pdf = "http://purl.org/censi/research/201510-monotone/3-ResourceAwareRoboticApplications.pdf",
        institution = "Laboratory for Information and Decision Systems/MIT"
    }</pre></p>
    <div class='desc'>
        
        
    </div><div style='clear:both'></div>
</div>
-->

<style type='text/css'>

div.pub-ref-compact { 
    font-family: sans-serif; font-size: smaller;
    width: 150%;
}

p.pub-ref-short {
    font-family: sans-serif;
    /*font-size: smaller;*/
}
p.pub-ref-short span.title { font-weight: bold;}

pre.pub-ref-bibtex { overflow: hidden;  font-size: 8pt;}
a.pub-ref-bibtex-link:before {content: " ";}

p.pub-ref-short span.links:before { content: "["; }
p.pub-ref-short span.links:after { content: "]"; }
p.pub-ref-short span.links span:after  { content: ", ";}
p.pub-ref-short span.links span:last-child:after { content: "";}
 

div.pub-ref-desc {
    padding-bottom: 1em;
}


div.pub-ref-desc div.desc { 
    margin-left: 1.5em;
    margin-right: 1.5em;
    display: block;
    overflow: auto; /* contains the floating img below */
}

div.pub-ref-compact img.icon {
    clear: left;
    float: left;
    margin-right: 1em;
    width: 4em;
    padding: 0;
    margin-bottom: 1em;
            border: solid 0px #888888;
        box-shadow: 2px 2px 8px #888888;

}

div.pub-ref-desc img.icon { 
    clear: left;
    float: left;
    margin-right: 1em;
    
    width: 7em;
    padding: 0;
    margin-bottom: 1em;
            border: solid 0px #888888;
        box-shadow: 2px 2px 8px #888888;
}

/* Publications previews */
div.pub_ref_page div.previews div.pdf-preview {
    text-align: center;
    margin: 1em;
    width: 8em;
    display: block;
    float: left;
}

div.pub_ref_page div.previews div.pdf-preview img {
    width: 8em;
    border: solid 1px #888888;
    box-shadow: 2px 2px 5px #888888;
}

div.pub_ref_page div.after-previews  {
    clear: both;
    display: block;
}

</style>
