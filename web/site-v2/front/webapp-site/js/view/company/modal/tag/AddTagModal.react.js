var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../../modal/Modal.react');

var AddTagModal = React.createClass({

    render(){
        return  <Modal id="add-tag-modal"
                       name="添加标签"
                       type="addTag"
                       comfirmName="添加"
                />
    }

});


module.exports = AddTagModal;