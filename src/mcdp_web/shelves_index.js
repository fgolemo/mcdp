function click(shelfname) {
    console.log('click ' + shelfname);
        $('#contents-'+shelfname).toggle();
}
function setup(shelfname) {

    $(document).ready(function() {
        console.log("init "+ shelfname);
    	$( "#button-" + shelfname ).button();
    	$( "#button-" + shelfname ).click(function() { click(shelfname); });
    });
}
