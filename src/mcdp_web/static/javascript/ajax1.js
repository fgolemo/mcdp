/* Utils for AJAX */

function ajax_send(url, payload, on_comm_failure, on_proc_failure, on_success) {
    /* Payload is a str-str dictiornary 

        on_comm_failure: when the call ends

        on_proc_failure: we got the data back, but data['ok'] was false
        on_success: data['ok'] = True; everything cool.
    */
    function failure(error) { 
        //console.log('Request to server failed.')
        if (on_comm_failure != null) {
            on_comm_failure(error);    
        }
        
    }
    function success(data) {
        if(data['ok']) {
            //console.log('Request to MCDP succeeded.')
            if (on_success != null) {
                on_success(data);
            }
        } else {
            // console.log('Request to MCDP failed.');
            // console.log(data);
            if (on_proc_failure != null) {
                on_proc_failure(data);
            }
        }
    }
    jQuery.ajax({
        url     : url,
        type    : 'POST',
        data: JSON.stringify(payload),
        contentType: 'application/json; charset=utf-8',
        success : success,
        error : failure,
    });
}



// function ajax_success(data) {
//     if (data['ok']) {
//         console.log(data);
//         $('#output_error').hide();
//         $('#output_success').show();
                 
//         $('#error').html('');
//         $('#output_raw').html(data['output_raw']);
//         $('#output_formatted').html(data['output_formatted']);
//         $('#output_parsed').html(data['output_parsed'])
//         $('#output_space').html(data['output_space'])

//     } else {
//     	$('#output_success').hide();
//         $('#output_error').show();
        
//         error = data['error']
//     	console.log(error);
//     	$('#error').html(error);

//         $('#output_raw').html();
//         $('#output_formatted').html();
//         $('#output_parsed').html();
//         $('#output_space').html();
// 	}
// }
    	
// function ajax_failure(error) {
// 	console.log(error);
// 	$('#error').html(error);
// }
