button_hide = 'button#hide';
code = '#code'

function hide_click() {
    $(code).toggle();

    var hidden = $( code).is( ":hidden" );

    right = 'td#right';
    if(hidden) {
        $(button_hide).text('show code');
        $(right).css('width', '100%');
    }
    else
    {
        $(button_hide).text('hide code');
        $(right).css('width', '');
    }

}

function syntax_init() {
    $(".make_button").button();

    $(button_hide).click(hide_click);

    // $( "a" ).animate({
    //       backgroundColor: "#aa0000",
    //     }, 1000 );

    // $("a").toggle( "highlight" );
    // $("a").effect( "pulsate" );
    // $("a").delay(200).fadeOut('slow').delay(50).fadeIn('slow');
}

$(document).ready(syntax_init);
