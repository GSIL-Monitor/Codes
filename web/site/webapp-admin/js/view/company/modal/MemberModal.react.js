var React = require('react');
var Modal = require('../../modal/Modal.react.js');


var MemberAction = require('../../../action/MemberAction');
var MemberStore = require('../../../store/MemberStore');

var MemberModal = React.createClass({
    render(){
        return(
            <div>
                <Modal id="modal-update"
                       name="确认更新"
                       comfirm={this.handleComfirm} />

                <Modal id="modal-delete"
                       name="确认删除"
                       comfirm={this.handleDelete} />
            </div>
        )
    },

    handleComfirm(){
        var store = MemberStore.get()
        MemberAction.update(store.members[store.idx]);
    },

    handleDelete(){
        var store = MemberStore.get();
        MemberAction.delete(store.members[store.idx].rel);
    },

});


module.exports = MemberModal;
