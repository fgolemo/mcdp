function click_dismiss() {
    id = $(this).attr('parent');
    console.log('clicked '+ id);
    cookie_name = tip_cookie(id);
    tip = $('#'+id);
    Cookies.set(cookie_name, tip.text());
    tip.hide();
}

function tip_cookie(id) {
    return 'hide-tip-' + id;
}

function reset_tip_cookies() {
    for(cookie in Cookies.get()) {
        if (cookie.startsWith('hide-tip')) {
                Cookies.remove(cookie);
        }
    }
}

function init_tip() {
    id = $(this).attr('id');
    cookie_name = tip_cookie(id);

    if(Cookies.get(cookie_name) != undefined) {
        $(this).hide();
        return;
    }
    btn = $('<button>Dismiss</button>');
    btn.button();
    btn.attr('parent', id);
    btn.click(click_dismiss);
    $(this).append(btn);
    options = {
        'duration': 1000,

    }
    $(this).show(options);
}

function init_tips() {
    $(".tip").each(init_tip);
}

$(document).ready(init_tips);
