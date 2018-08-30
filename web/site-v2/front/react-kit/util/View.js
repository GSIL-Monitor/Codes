var $ = require('jquery');
var Functions = require('./Functions');

$(document).ready(function () {
    $(window).bind("load resize scroll", function () {
        fix_height();
    });

    $('html').click(function() {
        $('.pop-inner, .pop-investor, .day-picker, .select-menu-modal').hide();
        $('.search-hint, .search-company-hint, .search-location-hint, .search-tag-hint, .search-investor-hint ').hide();
        $('.mark-list, .div-note').hide();
        $('.user-mark, .user-score, .user-note').show();
    });

    if(Functions.browserVersion() == 'mobile'){
        $('html').click(function() {
            $('.search-hint').hide();
        });
    }

});



function fix_height() {
    var windowHeight = $( window ).height();
    var docHeight = $(document).height();

    var windowWidth = $( window ).width();
    var docWidth = $(document).width();

    if (windowHeight > 500){
        $('.page-wrapper, .m-page-wrapper').css("min-height", windowHeight-120 +'px');
        $('.search-wrapper').css("min-height", windowHeight-180 +'px');
    }


    $('.sidebar, .modal, .modal-mask').css('height', docHeight+'px');
    $('.modal-body').css('max-height', windowHeight-100+'px');
    $('.modal-content').css('max-height', windowHeight-160+'px');
    $('.modal-body ').css('left', (windowWidth-800)/2+'px');
    $('.warn-body ').css('left', (windowWidth-600)/2+'px');
    if(windowWidth > 1000){
        $('.m-modal-body').css('left', (windowWidth-800)/2+'px');
    }



    var scrollTop = $(window).scrollTop();
    if( scrollTop > 600){
        $('.scroll-top').css('display', 'block');
    }else{
        $('.scroll-top').css('display', 'none');
    }


    // note
    $('.div-note, .note-list').css('max-height', windowHeight-380+'px');
    if(windowWidth < 1320){
        $('.div-note, .add-note-textarea').css('width', (windowWidth-1080)/2+180+'px');
    }else{
        $('.div-note, .add-note-textarea').css('width', '300px');
    }


    // user operate
    //$('.user-operate').css('margin-left', '100px').show();
    //if(Functions.browserVersion() != 'mobile')
    //    $('.user-operate').css('top', '130px');

}



const View = {
    fix(){
        fix_height();
    },

    fix_product(e){
        var wrapperHeight = $('.page-wrapper').height();
        var productNav = $('.product-nav').offset();
        if(productNav != undefined){
            var distance = wrapperHeight - productNav.top;
            var mouseTop = e.pageY;
            //console.log(mouseTop);
            //console.log(productNav.top);

            if(distance < 500){
                $('.page-wrapper').css("min-height", distance + 600 +'px')
            }
        }
    },

    bottomLoad(distance){
        var scrollTop = $(window).scrollTop();
        var scrollHeight = $(document).height();
        var windowHeight = $(window).height();
        if(scrollTop + windowHeight > (scrollHeight -distance) ){
            return true;
        }
        return false;
    }

};

module.exports = View;






