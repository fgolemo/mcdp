
The MD parsing cannot even deal with this:

<div>
    <div>
    </div> <!-- mistaken for closure of first -->
</div>


Look here for a fix: `http://stackoverflow.com/questions/7693535/what-is-a-good-xml-stream-parser-for-python`