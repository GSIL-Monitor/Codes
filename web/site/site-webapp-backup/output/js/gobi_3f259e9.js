$(document).ready(function(){function a(){var a=$("body > #wrapper").height()-61;$(".sidebard-panel").css("min-height",a+"px");var e=$("nav.navbar-default").height(),i=$("#page-wrapper").height(),s=$(window).height();$("#page-wrapper").css("min-height",s+"px"),null==e&&null==i&&$("#page-wrapper").css("min-height","700px"),e>i&&$("#page-wrapper").css("min-height",e+"px"),i>e&&$("#page-wrapper").css("min-height",s+"px"),i>e&&e>s&&$("#page-wrapper").css("min-height",i+"px"),e==i&&s>e&&$("#page-wrapper").css("min-height",s+"px")}$(window).bind("load resize scroll",function(){$("body").hasClass("body-small")||a()}),$(window).scroll(function(){$(window).scrollTop()>0&&!$("body").hasClass("fixed-nav")?$("#right-sidebar").addClass("sidebar-top"):$("#right-sidebar").removeClass("sidebar-top")}),setTimeout(function(){a()})}),$(function(){function a(){var a=$("#page-wrapper").height();a>1100&&$(".to-top").css("display","block")}$(window).bind("load resize",function(){$(this).width()<1e3&&$("body").addClass("mini-navbar"),$(this).width()<769?($("body").removeClass("mini-navbar"),$("body").addClass("body-small")):$("body").removeClass("body-small")}),$("html").click(function(){$(".search-span").hide(),$(".list-search-dropdown").hide()});var e={x:-1,y:-1};$(document).mousemove(function(i){e.x=i.pageX,e.y=i.pageY,i.pageY>800?a():i.pageY<700&&$(".to-top").css("display","none")})});