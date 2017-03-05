
function new_model() {
    url = url_base + 'models/new/';
    prompt_user('model', url, "Create new MCDP");
}

function new_template() {
    url = url_base + 'templates/new/';
    prompt_user('template', url, "Create new template");
}

function new_value() {
    url = url_base + 'values/new/';
    prompt_user('value', url, "Create new value");
}

function new_poset() {
    url = url_base + 'posets/new/';
    prompt_user('poset', url, "Create new poset");
}

$(document).ready(function() {
    options = {
        position: {
            my: "left top",
            at: "right top"
        }
    };
    $('#menu').menu(options);
    $('#menu').css('visibility', 'visible');
    $("#home").css('visibility', 'visible');

    $('#new_model').click(new_model);
    $('#new_poset').click(new_poset);
    $('#new_template').click(new_template);
    $('#new_value').click(new_value);
    $("#outer").show();
});
