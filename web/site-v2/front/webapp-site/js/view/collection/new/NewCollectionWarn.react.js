var React = require('react');
var $ = require('jquery');

var Warn = require('../../modal/Warn.react');

var NewCollectionWarn = React.createClass({

    render(){

        return  <Warn id="new-collection-warn"
                      name="提示"
                      content= ""
                      comfirm = {this.comfirm}
            />
    },

    comfirm(){
        $('#new-collection-warn').hide();
        //CompanyActions.deleteCompany();
    }

});


module.exports = NewCollectionWarn;