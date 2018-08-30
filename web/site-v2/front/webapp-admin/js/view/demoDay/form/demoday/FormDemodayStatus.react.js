var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var FormSelect =require('../FormSelect.react');
var DemodayUtil = require('../../../../util/DemodayUtil');

const FormDemodayStatus = React.createClass({

    render(){
        return (
            <div className="admin-demoday-row">
                <div><span> {this.props.label}:</span></div>
                <div className={this.props.className}>
                    <FormSelect    name='status'
                                   value={this.props.value}
                                   select={DemodayUtil.status}
                                   onChange={this.props.onChange}
                        />

                </div>
            </div>
        )
    }


});


module.exports = FormDemodayStatus;