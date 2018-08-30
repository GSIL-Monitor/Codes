var React = require('react');
var Modal = require('../../modal/Modal.react.js');


var InvestorActions = require('../../../reflux/InvestorActions');
var InvestorStore = require('../../../reflux/InvestorStore');

var UpdateModal = React.createClass({
    render(){
        return(
            <div>
                <Modal id="modal-update"
                       name="确认修改"
                       comfirm={this.handleComfirm} />

                <Modal id="modal-delete"
                       name="确认删除"
                       comfirm={this.handleClean} />
            </div>
        )
    },

    handleComfirm(){
        InvestorActions.update();
    },

    handleClean(){
        InvestorActions.delete();
    },

});


module.exports = UpdateModal;
