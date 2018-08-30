var React = require('react');
var Modal = require('../../modal/Modal.react.js');


var CompanyAction = require('../../../action/CompanyAction');
var CompanyStore = require('../../../store/CompanyStore');

var CompanyModal = React.createClass({
    render: function(){
        return(
            <div>
                <Modal id="modal-update" name="确认更新" comfirm={this.handleComfirm} />
                <Modal id="modal-reset" name="确认还原" comfirm={this.handleReset} />
            </div>
        )
    },

    handleComfirm: function(){
        CompanyAction.updateDB(CompanyStore.get());
    },

    handleReset: function(){
        CompanyAction.reset();
    }

});


module.exports = CompanyModal;
