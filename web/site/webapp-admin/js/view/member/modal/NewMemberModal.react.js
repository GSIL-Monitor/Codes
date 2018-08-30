var React = require('react');
var Modal = require('../../modal/Modal.react.js');


var NewAction = require('../../../action/member/NewAction');
var NewMemberStore = require('../../../store/member/NewMemberStore');

var NewMemberModal = React.createClass({
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
        var store = NewMemberStore.get()
        NewAction.add(store.current);
    },

    handleClean(){
        NewAction.clean();
    },

});


module.exports = NewMemberModal;
