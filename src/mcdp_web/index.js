function click_show_available() {
    $('#available').show();
    $('button#show-available').hide();
}

function init_index() {
    $('button#show-available').button().click(click_show_available);
}
$(document).ready(init_index);
