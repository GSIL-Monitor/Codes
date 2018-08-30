var React = require('react');
var $ = require('jquery');

var Modal = require('./Modal.react');

const DateModal = React.createClass({
    render(){
        return(
            <Modal id="date-modal" name="创立时间" content="date" comfirm={this.comfirm} />
        )
    },

    comfirm(){
        $('.modal').hide();
    }
});

module.exports = DateModal;