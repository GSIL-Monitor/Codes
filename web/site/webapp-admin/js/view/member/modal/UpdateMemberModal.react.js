var React = require('react');
var Modal = require('../../modal/Modal.react.js');


var MemberActions = require('../../../reflux/MemberActions');
var MemberStore = require('../../../reflux/MemberStore');

var UpdateMemberModal = React.createClass({
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
        MemberActions.update();
    },

    handleClean(){
        MemberActions.delete();
    },

});


module.exports = UpdateMemberModal;
