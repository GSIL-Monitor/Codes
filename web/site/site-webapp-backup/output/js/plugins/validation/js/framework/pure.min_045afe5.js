!function(e){FormValidation.Framework.Pure=function(o,a){a=e.extend(!0,{button:{selector:'[type="submit"]',disabled:"pure-button-disabled"},err:{clazz:"fv-help-block",parent:"^.*pure-control-group.*$"},icon:{valid:null,invalid:null,validating:null,feedback:"fv-control-feedback"},row:{selector:".pure-control-group",valid:"fv-has-success",invalid:"fv-has-error",feedback:"fv-has-feedback"}},a),FormValidation.Base.apply(this,[o,a])},FormValidation.Framework.Pure.prototype=e.extend({},FormValidation.Base.prototype,{_fixIcon:function(e,o){var a=this._namespace,t=(e.attr("type"),e.attr("data-"+a+"-field")),l=this.options.fields[t].row||this.options.row.selector,r=e.closest(l);0===r.find("label").length&&o.addClass("fv-icon-no-label")}})}(jQuery);