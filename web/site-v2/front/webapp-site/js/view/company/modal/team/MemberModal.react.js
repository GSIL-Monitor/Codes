var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../../modal/Modal.react');
var Functions = require('../../../../../../react-kit/util/Functions');
var MemberStore = require('../../../../store/company/MemberStore');

var MemberModal = React.createClass({

    mixins: [Reflux.connect(MemberStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        return  <Modal id="member-modal"
                       name="成员详细信息"
                       type="member"
                       data= {state.data.selected}
                />
    }

});


module.exports = MemberModal;