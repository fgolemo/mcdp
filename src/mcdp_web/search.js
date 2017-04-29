
function init_list() {
    var options = {
        valueNames: [ 'name', 'desc' ],
        listClass: 'mylist'
    };

    var userList = new List('container', options);
    // console.log('userList ok')
}

function add_to_table(dataObject) {
    var name = dataObject.name;
    var url = dataObject.url;
    var desc = dataObject.desc;
    // console.log(url);

    li = $('<li>');
    s = $('<span>').text(name).attr('class', 'name tohide');
    li.append(s);
    desc = $($.parseHTML(desc));
    descw = $('<span>')
    descw.append(desc)
    descw.attr('class', 'desc');
    li.append(descw);

    $(".mylist").append(li);

}

function init_search() {
    $.ajax({
        url: ':query',
        type: 'GET',
        data: {
            // "keyword" : $("#keywordElementID").val(), /* other variables */
        },
        dataType: 'JSON',
        success:
             function( returnedJSON  ){
                 //use returned text here
                 //to loop through data objects from API
                 $.each( returnedJSON.data, function( index , dataObject ){
                     add_to_table(dataObject);
                 });

                 init_list();
            }
    });
}


$( document ).ready(init_search) ;
// $(init_search);
