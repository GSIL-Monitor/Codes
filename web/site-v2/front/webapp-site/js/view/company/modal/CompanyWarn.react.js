var React = require('react');
var $ = require('jquery');

var Warn = require('../../modal/Warn.react');

var CompanyWarn = React.createClass({

    render(){

        return  <Warn id="company-warn"
                      name="提示"
                      content= ""
                      comfirm = {this.comfirm}
                />
    },

    comfirm(){
        $('#company-warn').hide();
        //CompanyActions.deleteCompany();
    }

});


module.exports = CompanyWarn;