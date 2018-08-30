var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../modal/Modal.react');

var OrgPreScoresModal = React.createClass({

    render(){
        return  <Modal id="preScores"
                       name="打分详情"
                       type="preScores"
            />
    }

});


module.exports = OrgPreScoresModal;