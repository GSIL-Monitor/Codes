var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../modal/Modal.react');

var RejectOrgListModal = React.createClass({

    render(){

        return  <Modal id="rejectOrg-modal"
                       name="添加参会机构"
                       type="rejectOrg"
            />
    }

});


module.exports = RejectOrgListModal;