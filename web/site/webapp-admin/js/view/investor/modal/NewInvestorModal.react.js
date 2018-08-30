var React = require('react');
var Modal = require('../../modal/Modal.react.js');


var InvestorActions = require('../../../reflux/InvestorActions');

var NewInvestorModal = React.createClass({
    render(){
        return(
            <div>
                <Modal id="modal-add"
                       name="确认添加"
                       comfirm={this.handleComfirm} />

                <Modal id="modal-clean"
                       name="确认清除"
                       comfirm={this.handleClean} />
            </div>
        )
    },

    handleComfirm(){
        InvestorActions.add();
    },

    handleClean(){
        InvestorActions.clean();
    },

});


module.exports = NewInvestorModal;
