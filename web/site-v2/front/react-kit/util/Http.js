var $ = require('jquery');

var View = require('./View');

const Http = {
    ajax(payload, url, callback){

        View.fix();

        $.ajax({
            url: url,
            method: 'POST',
            data: JSON.stringify(payload),
            contentType: "application/json",
            cache: false,
            timeout: 5000,
            success: function (result) {

                callback(result);
            },
            error: function (data) {

                //$('.hint').html('加载超时').show().fadeOut(2000);
                console.log(data);
            }
        });
    },


    ajaxAndMask(payload, url, callback){

        $('.mask').show();
        //document.body.style.overflow = 'hidden';
        $(window).scrollTop(0);
        View.fix();

        $.ajax({
            url: url,
            method: 'POST',
            data: JSON.stringify(payload),
            contentType: "application/json",
            cache: false,
            timeout: 5000,
            success: function (result) {
                callback(result);

                $('.mask').fadeOut(100, function(){
                    //document.body.style.overflow = 'auto';
                });

            },
            error: function (data) {
                console.log(data);
                $('.mask').fadeOut(100, function(){
                    //document.body.style.overflow = 'auto';
                    $('.hint').html('加载失败').show().fadeOut(3000);
                    $('.page-wrapper > div').html('<div class="load-fail">重新加载' +
                        '<i class="fa fa-refresh fa-lg m-l-10"></i></div>');
                    $('.load-fail').click(function(){
                        window.location.reload();
                    })
                });
            }
        });
    },

    ajaxSearch(payload, url, callback, errorback){

        $('.mask').show();

        var searchBody = $('.search-main').offset();
        if(searchBody != undefined){
            if($(window).scrollTop() > searchBody.top){
                $(window).scrollTop(searchBody.top);
            }
        }
        View.fix();

        $.ajax({
            url: url,
            method: 'POST',
            data: JSON.stringify(payload),
            contentType: "application/json",
            cache: false,
            timeout: 5000,
            success: function (result) {
                callback(result);

                $('.mask').fadeOut(100, function(){
                    //document.body.style.overflow = 'auto';
                });

                return true;
            },
            error: function (data) {
                errorback(data);

                $('.mask').fadeOut(100, function(){
                    //document.body.style.overflow = 'auto';
                    $('.hint').html('加载失败').show().fadeOut(3000);
                });
            }
        });
    }

};


module.exports = Http;