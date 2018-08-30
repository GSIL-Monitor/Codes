var React = require('react');
var $ = require('jquery');

var Warn = require('../../modal/Warn.react');
var CompanyActions = require('../../../action/CompanyActions');

var WarnModal = React.createClass({

    render(){

        return  <Warn id="delete-company-warn"
                      name="确认删除"
                      content= "确认删除该公司？"
                      comfirm = {this.comfirm}
                />
    },

    comfirm(){
        //CompanyActions.deleteCompany();
    }

});


module.exports = WarnModal;