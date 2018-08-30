var AppDispatcher = require('../dispatcher/AppDispatcher');
var $ = require('jquery');


const Http = {
    get(id, url, type){
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            timeout: 10000,
            success: function (data) {
                AppDispatcher.dispatch({
                    actionType: type,
                    id: id,
                    data: data
                });

                var windowHeigh = $( window ).height();
                $('.page-wrapper').css("min-height", windowHeigh-80 +'px');

            },
            error: function (data) {
                console.error(data);
                var windowHeigh = $( window ).height();
                $('.page-wrapper').css("min-height", windowHeigh-80 +'px');
            }
        });
    },

    put: function(url, type, data, hint) {
        $('.mask').show();
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(data),
            contentType:"application/json",
            cache: false,
            timeout: 10000,
            success: function(result) {
                //console.log(result)
                AppDispatcher.dispatch({
                    actionType: type,
                    data: data
                });

                $('.hint').show()
                    .html(hint)
                    .delay(1500)
                    .hide(0);

                $('.mask').hide();
            },
            error: function(data) {
                console.log(data);
                $('.mask').hide();
            }
        });

    },

    add(url, type, data, hint) {
        $('.mask').show();
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(data),
            contentType: "application/json",
            cache: false,
            timeout: 10000,
            success: function(result) {
                data.id = result.id;

                AppDispatcher.dispatch({
                    actionType: type,
                    data: data
                });

                $('.hint').show()
                    .html(hint)
                    .delay(1500)
                    .hide(0);

                $('.mask').hide();
            },
            error: function(data) {
                console.log(data);
                $('.mask').hide();
            }
        });

    },

    addAndReturnResult(url, type, data, hint) {
        $('.mask').show();
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(data),
            contentType: "application/json",
            cache: false,
            timeout: 10000,
            success: function(result) {
                //console.log(result);
                AppDispatcher.dispatch({
                    actionType: type,
                    data: result
                });

                $('.hint').show()
                    .html(hint)
                    .delay(1500)
                    .hide(0);

                $('.mask').hide();
            },
            error: function(data) {
                console.log(data);
                $('.mask').hide();
            }
        });

    },

    getList(url, data, type){
        $.ajax({
            url: url,
            method: 'POST',
            data: data,
            contentType: "application/json",
            cache: false,
            timeout: 10000,
            success: function (data) {
                AppDispatcher.dispatch({
                    actionType: type,
                    data: data
                });

                var windowHeigh = $( window ).height();
                $('.page-wrapper').css("min-height", windowHeigh-80 +'px');

            },
            error: function (data) {
                console.error(data);
                var windowHeigh = $( window ).height();
                $('.page-wrapper').css("min-height", windowHeigh-80 +'px');
            }
        });
    },

};


module.exports = Http;