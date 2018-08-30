
$(document).ready(function () {
    
    $(window).bind("load resize scroll", function() {
        if(!$("body").hasClass('body-small')) {
               fix_height();
        }
    })

    // Move right sidebar top after scroll
    $(window).scroll(function(){
        if ($(window).scrollTop() > 0 && !$('body').hasClass('fixed-nav') ) {
            $('#right-sidebar').addClass('sidebar-top');
        } else {
            $('#right-sidebar').removeClass('sidebar-top');
        }
    });

    setTimeout(function(){
        fix_height();
    });
    
});

// Minimalize menu when screen is less than 768px
$(function() {
    $(window).bind("load resize", function() {
    	if ($(this).width() < 1000) {
    		$('body').addClass('mini-navbar')
    	}
    	
    	if ($(this).width() < 769) {
    		$('body').removeClass('mini-navbar')
            $('body').addClass('body-small')
        } else {
            $('body').removeClass('body-small')
        }
    	
    })
    
    $('html').click(function() {
    	$('.search-span').hide();
    	$('.list-search-dropdown').hide();
        $('.tt-dropdown-menu').hide();
	});
    
    
    var currentMousePos = { x: -1, y: -1 };
    $(document).mousemove(function(event) {
        currentMousePos.x = event.pageX;
        currentMousePos.y = event.pageY;
        if(event.pageY > 800){
        	to_top();
        }else if(event.pageY <700){
        	$('.to-top').css('display', 'none');
        }
    });
    
    

})


 // Full height of sidebar
function fix_height() {
    var heightWithoutNavbar = $("body > #wrapper").height() - 61;
    $(".sidebard-panel").css("min-height", heightWithoutNavbar + "px");

    var navbarHeigh = $('nav.navbar-default').height();
    var wrapperHeigh = $('#page-wrapper').height();
    var windowHeigh = $( window ).height();
    
    
    $('#page-wrapper').css("min-height", windowHeigh +'px');
    
    if(navbarHeigh == null && wrapperHeigh ==null){
    	$('#page-wrapper').css("min-height", "700px");
    }

    if(navbarHeigh > wrapperHeigh){
        $('#page-wrapper').css("min-height", navbarHeigh + "px");
    }

    if(navbarHeigh < wrapperHeigh){
        $('#page-wrapper').css("min-height", windowHeigh + "px");
    }
    if(navbarHeigh < wrapperHeigh && navbarHeigh > windowHeigh){
    	$('#page-wrapper').css("min-height", wrapperHeigh + "px");
    }

    if(navbarHeigh == wrapperHeigh && navbarHeigh < windowHeigh){
    	$('#page-wrapper').css("min-height", windowHeigh  + "px");
    }
    
}

function to_top(){
	var height = $('#page-wrapper').height();
	if(height > 1100){
		$('.to-top').css('display', 'block');
	}
}
