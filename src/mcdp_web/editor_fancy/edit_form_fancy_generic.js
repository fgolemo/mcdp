var saved_text = {{source_code_json | safe}};
var white_background = '{{static}}/white.png';
var title_s = "{{navigation['current_thing']}}";
var title_u = "*{{navigation['current_thing']}}";
var icon_s = '{{static}}/favicon_editor_{{url_part}}_saved.png';
var icon_u = '{{static}}/favicon_editor_{{url_part}}_unsaved.png';
var format = "{{format}}";

var last_text_sent_to_server = null;
var last_rendered_text = null;
var timeoutID = null;
var parsing_wait_ms = 800;
var string_with_suggestions = null;
var display_timeout = 2000;
var saved = true;
var bg_color_parsing =  '#fee';
var red_dot = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='

function nodefault(event) {
    event.preventDefault();
}

function editor_init1() {
    $("button").button().click(nodefault);
    update_save_button_color();

    $(document).on('keydown', '#editor', editor_keydown);

    $("#editor").keyup(keyup);
    $("button#close").click(click_button_close);
    $("button#save").click(click_button_save);
    $("button#discard").click(click_button_discard);
    $("button#revert").click(click_button_revert);
    $("button#apply_suggestions").click(click_apply_suggestions);

    text0 = current_text()
    console.log('asking server');
    image_set_temporary();
    try_to_parse(text0);

    $('#allcontents').css('visibility', 'visible');
}

$(document).ready(editor_init1);

function editor_keydown(e) {
    function indentation_at_last_line(pos0) {
        last = text.substring(0, pos0);
        lines = last.split("\n");
        last_line = lines[lines.length - 1];
        nspaces = last_line.search(/\S|$/);
        return nspaces;
    }
    pos = getCaretCharacterOffsetWithin($("#editor").get(0));

    /*ctrl+s or command+s*/
    if ((e.metaKey || e.ctrlKey) && e.keyCode == 83) {
        e.preventDefault();
        click_button_save();
    }

    //detect 'tab' key
    if (e.keyCode == 9) {
        //add tab with 4 spaces
        document.execCommand('insertHTML', false, ' '.repeat(4));
        //prevent focusing on next element
        e.preventDefault();
    }
    // fix for firefox which creates <br/>
    // when enter is pressed
    if (e.keyCode == 13) { //enter
        nspaces = indentation_at_last_line(pos);
        if (last_line.includes('{'))
            nspaces += 4;

        indentation = ' '.repeat(nspaces);
        document.execCommand('insertHTML', false, "\n" + indentation);

        e.preventDefault();
    }
    /*
    if (e.keyCode == 219) { // open brace
        nspaces = 4 + indentation_at_last_line(pos);
        indentation = ' '.repeat(nspaces);
        insert = '{\n' + indentation;
        document.execCommand('insertHTML', false, insert);
        e.preventDefault();
    }
    if (e.keyCode == 221) { // close brace
        document.execCommand('insertHTML', false, "}");
        e.preventDefault();
    }*/
}


function current_text() {
    text = $("#editor").text();
    return text;
}

function update_save_button_color() {
    text = current_text();

    if (text == saved_text) {
        $('button#save').css('color', '');
        $('button#revert').css('color', '');
        $('button#revert').button('disable');
        $('button#save').button('disable');
        document.title = title_s;
        $('link[rel="icon"]').attr('href', icon_s);

    } else {
        $('button#save').css('color', 'red');
        $('button#revert').css('color', 'orange ');
        $('button#revert').button('enable');
        $('button#save').button('enable');
        document.title = title_u;
        $('link[rel="icon"]').attr('href', icon_u);
    }

    console.log(JSON.stringify(text));

    if (false) {
        ends_with_spaces = /\s+$/g.test(text);
        console.log(JSON.stringify(ends_with_spaces));
        console.log('ends_with_spaces ' + ends_with_spaces);
        if (ends_with_spaces) {
            $('#editor').addClass('endswithspace');
        } else {
            $('#editor').removeClass('endswithspace');
        }
    }
}

function keyup() {
    /* We do not ask for parsing every time a key is pressed */
    text = current_text();

    // do not do it twice
    if (text == last_rendered_text)
        return;
    if (text == last_text_sent_to_server)
        return;

    $('.unparsable').css('color', 'black');

    text_has_changed();

    string_with_suggestions = null;
    $('#apply_suggestions').hide();

    // and we wait that the user stops editing for parsing_wait_ms
    if (timeoutID != null)
        window.clearTimeout(timeoutID);

    timeoutID = window.setTimeout(try_to_parse_it, parsing_wait_ms);
}

function text_has_changed() {
    update_save_button_color();
    // $('button#save').disable();
    $('#around_editor').css('background-color', '#ffe');
    $('#syntax_error').hide();
    $('#syntax_error').html('');
    $('#language_warnings').html('');

    image_update_to(white_background);
    saved = false;
}

function image_update_to(src) {
    current = $("a#graph img").attr("src");
    if (current != src)
        $("a#graph img").attr("src", src);

}

function try_to_parse_it() {
    text = current_text();
    //console.log('asking server to parse ' + text);
    image_set_temporary();
    try_to_parse(text);
}

function on_comm_failure(error) {
    console.log('AJAX error');
    console.log(error);
    $('#comm_failure').html(error);
}

function update_text(highlight, pos) {

    $(".ui-tooltip").hide();
    $("#editor").html(highlight);
    $("#editor").tooltip();
    set_caret(pos);

    update_save_button_color();
}

function set_caret(pos) {
    editor = $("#editor").get(0);
    elements = get_elements(editor);

    if (pos >= elements.length) {
        pos = elements.length - 1;
        textNode = elements[pos]['text'];
        caret = elements[pos]['char'] + 1
    } else {
        e = elements[pos];
        textNode = e['text'];
        caret = e['char'];

        if (e == null) {
            console.log('Could not find element at range ' + pos);
            console.log(elements);
        }
    }

    var range = document.createRange();
    range.setStart(textNode, caret);
    range.setEnd(textNode, caret);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
}


function update_text_with_highlight(req_text, highlight) {
    // never change the user input!
    pos = getCaretCharacterOffsetWithin($("#editor").get(0));
    if (pos == null) {
        console.log('Cannot get element cursor.');
        pos = 0;
    }
    last_rendered_text = req_text;

    update_text(highlight, pos);
}

function still_relevant(req_text) {
    text = current_text();
    return req_text == text || req_text == string_with_suggestions;
}

function multiple_selection() {
    // Returns true if the user is selecting an area
    // So that we don't replace the text below

    function getSelectedText() {
        var text = "";
        if (typeof window.getSelection != "undefined") {
            text = window.getSelection().toString();
        } else if (typeof document.selection != "undefined" && document.selection.type == "Text") {
            text = document.selection.createRange().text;
        }
        return text;
    }
    text = getSelectedText();
    return text.length > 0;
}

function try_to_parse(s) {
    function on_proc_failure(res) {
        $('#syntax_error').html(res['error']);
        $('#syntax_error').show();
        $('#language_warnings').html(); /* XXX */
        $('#around_editor').css('background-color', bg_color_parsing);

        if ('highlight' in res) {
            res_text = res['request']['text']
            relevant = still_relevant(res_text);
            //console.log('relevant ' +relevant)
            if (relevant)
                update_text_with_highlight(res_text, res['highlight']);
            else {
                show_status('#server_status', 'Server is slow in responding...');
            }
        }
    }

    function on_success(res) {
        res_text = res['request']['text']
        relevant = still_relevant(res_text);

        if (!relevant || (res_text != last_text_sent_to_server)) {
            //console.log('Slow server: ignoring stale.');
            show_status('#server_status', 'Server is slow in responding...');
            return;
        }

        if (multiple_selection())
            return;

        image_set_text(res_text);

        string_with_suggestions = res['string_with_suggestions']
        if (null != string_with_suggestions) {
            if (string_with_suggestions != res_text) {
                $('#apply_suggestions').show();
            } else {
                $('#apply_suggestions').hide();
            }
        } else {
            $('#apply_suggestions').hide();
        }

        $('#around_editor').css('background-color', 'white');
        $('#syntax_error').hide();
        $('#syntax_error').html('');
        if ('language_warnings' in res) {
            $('#language_warnings').html(res['language_warnings']);
        }

        update_text_with_highlight(res_text, res['highlight']);
    }

    last_text_sent_to_server = s;
    ajax_send("ajax_parse", {'text': s},
        on_comm_failure, on_proc_failure, on_success);
}

function click_button_discard(res) {
    // Override safety mechanism
    saved = true;
    location.reload();
}

function click_button_revert(res) {
    // Override safety mechanism
    console.log("revert to text " + saved_text);
    // try_to_parse(saved_text);
    s = saved_text;
    update_text_with_highlight(s, s);
    try_to_parse_it();
}

function click_button_close(res) {
    click_button_save();
    saved = true;
    url = '../syntax/'
    window.location = url;
}

function click_button_save() {
    $('#save_status').html('saving...');
    data = {
        'text': current_text()
    };
    // console.log('data');
    // console.log(data);
    ajax_send("save", data, on_comm_failure,
        click_button_save_failure, click_button_save_success);
}

function click_button_save_success(res) {
    show_status('#save_status', 'success');
    console.log()
    console.log('success');
    console.log(JSON.stringify(res));
    /// XXX not if the text has changed in the mean time
    saved_text = res['saved_string'];
    update_save_button_color();
    saved = true;
}

function click_button_save_failure(res) {
    show_status('#save_status', 'failed');
    console.log('failure');
    console.log(res);
}

function show_status(selector, msg) {
    $(selector).html(msg);
    window.setTimeout(function() {
            $(selector).html('');
        },
        display_timeout);
}

function image_set_temporary() {
    image_update_to(white_background);
    // image_update_to(red_dot);
}

function image_set_text(text) {
    hash = hex_sha1(text);
    url = "graph."+hash+"." + format;
    $("a#graph img").prop("src", url);
}

function click_apply_suggestions() {
    if (string_with_suggestions != null) {
        try_to_parse(string_with_suggestions);
    }
}

function confirmExit() {
    if (!saved) {
        return "You did not save, do you want to do it now?";
    }
}
window.onbeforeunload = confirmExit;
