
var g_what = null;
var g_url_base = null;
var dialog = null;

// Prompts the user to create a new "what", which should be a valid identifier.
// function prompt_user(what, url_base)
// it then goes to /url_base/<name>
function prompt_user(what, url_base, prompt="Create new item") {
  g_what = what;
  g_url_base = url_base;
  $('#dialog-form').attr('title', prompt);
  $('#dialog-form').dialog('option', 'title', prompt);
  $('#dialog-form').data('dialog.title', prompt);
  dialog.dialog( "open" );
  // $('#dialog-form').tooltip( "disable" );

  $('.ui-dialog-buttonpane > button:last').focus();
}

function create_window(url) {
    // opens a tab/window
    // returns true on success
    var win = window.open(url, '_blank');
    if (win) {
        //Browser has allowed it to be opened
        win.focus();
        return true;
    } else {
        //Browser has blocked it
        alert('Please allow popups for this application.');
        return false;
    }
}

function valid_identifier(s) {
	var reg = /^[a-zA-Z_$][0-9a-zA-Z_$]*$/g;
	var match = reg.test(s);
	if(!match)
		return false;
	else
		return true;
}


function init_dialog() {
    options = {
        autoOpen: false,
        // height: 200,
        //width: 350,
        modal: true,
        buttons: { "create": dialog_create, "cancel": dialog_cancel },
        close: dialog_close
    }

    dialog = $( "#dialog-form" ).dialog(options);

    $('#dialog-form #name').keyup(function(e) {
        if (e.keyCode == 13) // enter
            dialog_create();
    });
}

$(document).ready(init_dialog);

function dialog_create() {
    var valid = true;
    $("#name").removeClass( "ui-state-error" );
    use = $( "#name" ).val();
    console.log(use);
    valid = valid && valid_identifier(use);
    if(valid) {
        dialog.dialog( "close" );
        url = g_url_base + use;
        //console.log("valid identifier, opening " + url);
        create_window(url);
        return true;
    } else {
        $("#form_error").text("Invalid identifier “"+use+"”.");
        return false;
    }
}

function dialog_cancel() {
    dialog.dialog( "close" );
}

function dialog_close() {
    $( "#name" ).removeClass( "ui-state-error" );
    // todo: reset
}




// old function
///
// function prompt_user0(what, url_base) {
//   s  = "Please enter the name for the new " + what + ":";
//   var name=prompt(s);
//   if(name == null) {
//   	return;
//   }
//   if(!valid_identifier(name)) {
//     msg = 'The string "'+name+'" is not a valid identifier.';
//   	alert(msg);
//   	return;
//   }
//   url = url_base + name;
//   var win = window.open(url, '_blank');
//   if (win) {
//       //Browser has allowed it to be opened
//       win.focus();
//   } else {
//       //Browser has blocked it
//       alert('Please allow popups for this application.');
//   }
// }
