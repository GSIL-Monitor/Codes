!function(o){FormValidation.Framework.Foundation=function(t,i){i=o.extend(!0,{button:{selector:'[type="submit"]',disabled:"disabled"},err:{clazz:"error",parent:"^.*((small|medium|large)-[0-9]+)\\s.*(columns).*$"},icon:{valid:null,invalid:null,validating:null,feedback:"fv-control-feedback"},row:{selector:".row",valid:"fv-has-success",invalid:"error",feedback:"fv-has-feedback"}},i),FormValidation.Base.apply(this,[t,i])},FormValidation.Framework.Foundation.prototype=o.extend({},FormValidation.Base.prototype,{_fixIcon:function(o,t){var i=this._namespace,n=o.attr("type"),a=o.attr("data-"+i+"-field"),e=this.options.fields[a].row||this.options.row.selector,r=o.closest(e);if("checkbox"===n||"radio"===n){var l=t.next();l.is("label")&&t.insertAfter(l)}0===r.find("label").length&&t.addClass("fv-icon-no-label")},_createTooltip:function(o,t,i){var n=this,a=o.data("fv.icon");a&&(a.attr("title",t).css({cursor:"pointer"}).off("mouseenter.container.fv focusin.container.fv").on("mouseenter.container.fv",function(){n._showTooltip(o,i)}).off("mouseleave.container.fv focusout.container.fv").on("mouseleave.container.fv focusout.container.fv",function(){n._hideTooltip(o,i)}),Foundation.libs.tooltip.create(a),a.data("fv.foundation.tooltip",a))},_destroyTooltip:function(o){var t=o.data("fv.icon");if(t){t.css({cursor:""});var i=t.data("fv.foundation.tooltip");i&&(i.off(".fndtn.tooltip"),Foundation.libs.tooltip.hide(i),t.removeData("fv.foundation.tooltip"))}},_hideTooltip:function(o){var t=o.data("fv.icon");if(t){t.css({cursor:""});var i=t.data("fv.foundation.tooltip");i&&Foundation.libs.tooltip.hide(i)}},_showTooltip:function(o){var t=o.data("fv.icon");if(t){var i=t.data("fv.foundation.tooltip");i&&(t.css({cursor:"pointer"}),Foundation.libs.tooltip.show(i))}}})}(jQuery);