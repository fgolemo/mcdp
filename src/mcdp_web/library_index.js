function click_show_previews() {
    $('#previews').show();
    console.log(all_images);
    for (var i in all_images) {
        x = all_images[i];
        target = x[1];
        src = x[0];

        tmpimg = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==';

        $(target).prop('src', tmpimg);
        $(target).prop('src', src);
    }
}

$(document).ready(function() {
    $("button#show_previews").button();
    $("button#show_previews").click(click_show_previews);

    $('#table_new_models').click(new_model);
    $('#table_new_posets').click(new_poset);
    $('#table_new_templates').click(new_template);
    $('#table_new_values').click(new_value);
    $('#allcontents').css('visibility', 'visible');

});

var all_images = [];
