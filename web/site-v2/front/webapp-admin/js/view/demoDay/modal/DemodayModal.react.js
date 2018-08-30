var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../modal/Modal.react');

var DemodayModal = React.createClass({

    render(){
        return  <Modal id="demoday-modal"
                       name="修改demoday信息"
                       type="demoday"
            />
    }

});


module.exports = DemodayModal;