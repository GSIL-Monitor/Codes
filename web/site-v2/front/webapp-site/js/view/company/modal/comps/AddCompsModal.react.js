var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../../modal/Modal.react');

var AddTagModal = React.createClass({

    render(){
        return  <Modal id="add-comps-modal"
                       name="添加竞争对手"
                       type="addComps"
                       comfirmName="添加"
                />
    }

});


module.exports = AddTagModal;