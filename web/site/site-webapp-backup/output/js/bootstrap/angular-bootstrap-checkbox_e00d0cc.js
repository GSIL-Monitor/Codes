"use strict";angular.module("ui.checkbox",[]).directive("checkbox",function(){return{scope:{},require:"ngModel",restrict:"E",replace:"true",template:"<button type=\"button\" ng-style=\"stylebtn\" class=\"btn btn-white\" ng-class=\"{'btn-xs': size==='default', 'btn-sm': size==='large', 'btn-lg': size==='largest'}\">"+'<span ng-style="styleicon" class="glyphicon" ng-class="{\'fa fa-check\': checked===true}"></span></button>',link:function(e,t,l,n){var a=t.next("span");e.size="default",e.stylebtn={},e.styleicon={width:"10px",left:"-1px"},void 0!==l.large&&(e.size="large",e.stylebtn={"padding-top":"2px","padding-bottom":"2px",height:"30px"},e.styleicon={width:"8px",left:"-5px","font-size":"17px"}),void 0!==l.larger&&(e.size="larger",e.stylebtn={"padding-top":"2px","padding-bottom":"2px",height:"34px"},e.styleicon={width:"8px",left:"-8px","font-size":"22px"}),void 0!==l.largest&&(e.size="largest",e.stylebtn={"padding-top":"2px","padding-bottom":"2px",height:"45px"},e.styleicon={width:"11px",left:"-11px","font-size":"30px"});var i=!0,o=!1;void 0!==l.ngTrueValue&&(i=l.ngTrueValue),void 0!==l.ngFalseValue&&(o=l.ngFalseValue),void 0!==e.name&&(t.name=e.name),e.$watch(function(){return n.$modelValue===i||n.$modelValue===!0?(n.$setViewValue(i),a.addClass("todo-completed")):n.$setViewValue(o),n.$modelValue},function(){e.checked=n.$modelValue===i},!0),t.bind("click",function(){e.$apply(function(){n.$modelValue===o?(n.$setViewValue(i),a.toggleClass("todo-completed")):(n.$setViewValue(o),a.toggleClass("todo-completed"))})})}}});