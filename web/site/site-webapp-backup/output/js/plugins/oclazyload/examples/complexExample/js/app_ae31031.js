"use strict";var App=angular.module("app",["ui.router","oc.lazyLoad"]).config(function(o,a,e,l){e.otherwise("/"),a.hashPrefix("!"),o.state("index",{url:"/",views:{lazyLoadView:{controller:"AppCtrl",templateUrl:"partials/main.html"}},resolve:{loadMyCtrl:["$ocLazyLoad",function(o){return o.load({name:"app",files:["js/AppCtrl.js"]})}]}}).state("modal",{parent:"index",resolve:{loadOcModal:["$ocLazyLoad","$injector","$rootScope",function(o,a,e){return o.load({name:"oc.modal",files:["bower_components/bootstrap/dist/css/bootstrap.css","bower_components/ocModal/dist/css/ocModal.animations.css","bower_components/ocModal/dist/css/ocModal.light.css","bower_components/ocModal/dist/ocModal.js","partials/modal.html"]}).then(function(){e.bootstrapLoaded=!0;var o=a.get("$ocModal");o.open({url:"modal",cls:"fade-in"})})}],setModalBtn:["loadOcModal","$rootScope","$ocModal",function(o,a,e){a.openModal=function(){e.open({url:"modal",cls:"flip-vertical"})}}]}}),a.html5Mode(!1),l.config({debug:!0,events:!0,modules:[{name:"gridModule",files:["js/gridModule.js"]}]})});