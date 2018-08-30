var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

const FormDemoday = React.createClass({

    render(){
        return (
            <div className="admin-demoday-row">
                <div><span> {this.props.label}:</span></div>
                <div className={this.props.className}><span> {this.props.data}</span></div>
            </div>
        )
    }


});


module.exports = FormDemoday;