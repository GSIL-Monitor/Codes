"use strict";angular.module("nouislider",[]).directive("slider",function(){return{restrict:"A",scope:{start:"@",step:"@",end:"@",callback:"@",margin:"@",ngModel:"=",ngFrom:"=",ngTo:"="},link:function(n,r){var t,a,l,e,o;return e=$(r),t=n.callback?n.callback:"slide",null!=n.ngFrom&&null!=n.ngTo?(a=null,o=null,e.noUiSlider({start:[n.ngFrom||n.start,n.ngTo||n.end],step:parseFloat(n.step||1),connect:!0,margin:parseFloat(n.margin||0),range:{min:[parseFloat(n.start)],max:[parseFloat(n.end)]}}),e.on(t,function(){var r,t,l;return l=e.val(),r=l[0],t=l[1],a=parseFloat(r),o=parseFloat(t),n.$apply(function(){return n.ngFrom=a,n.ngTo=o})}),n.$watch("ngFrom",function(n){return n!==a?e.val([n,null]):void 0}),n.$watch("ngTo",function(n){return n!==o?e.val([null,n]):void 0})):(l=null,e.noUiSlider({start:[n.ngModel||n.start],step:parseFloat(n.step||1),range:{min:[parseFloat(n.start)],max:[parseFloat(n.end)]}}),e.on(t,function(){return l=parseFloat(e.val()),n.$apply(function(){return n.ngModel=l})}),n.$watch("ngModel",function(n){return n!==l?e.val(n):void 0}))}}});