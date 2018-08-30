var $ = require('jquery');
var Required = {
    handleBlur(event){
        var value = event.target.value;
        var classList = event.target.classList;
        //满足条件下，只执行一次
        if((value==null||value.trim()=='')&&!classList[1]){
            $('#'+event.target.id).addClass(' required-border');
            var text='<span class="required-content m-l-5"><i class="fa fa-times-circle"/>必填</span>';
            $('#'+event.target.id).after(text);
        }
    },
    handleChange(event){
        var value = event.target.value;
        if(value!=null&&value.trim()!=''){
            $('#'+event.target.id).removeClass('required-border');
            $(event.target.nextSibling).remove();
        }
    },
};

module.exports = Required;


