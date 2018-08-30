var $ = require('jquery');

$(document).ready(function () {
    $(window).bind("load resize scroll", function () {
        fix_height();
    });

    $('html').click(function() {
        $('.pop-inner, .pop-investor, .day-picker, .select-menu-modal, .search-hint').hide();
    });

});



function fix_height() {
    var windowHeight = $( window ).height();
    var docHeight = $(document).height();

    if (windowHeight > 500){
        $('.page-wrapper').css("min-height", windowHeight-80 +'px');
    }

    $('.sidebar, .modal, .modal-mask').css('height', docHeight+'px');
    $('.modal-body').css('max-height', windowHeight-120+'px');
    $('.modal-content').css('max-height', windowHeight-220+'px');


    var windowWidth = $( window ).width();
    var docWidth = $(document).width();

    if(windowWidth < 1000){
        $('.modal-body ').css('left', '100px');
    }else{
        $('.modal-body ').css('left', '20%');
    }


}





