/**
 * Created by haiming on 16/2/3.
 */
var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../../../react-kit/util/Functions');
var FormTextarea = require('../FormTextarea.react');

const Work = React.createClass({


    render(){

        return <FormTextarea label='工作经历'
                             name='work'
                             value={this.props.data}
                             className='form-input-full'
                             onChange={this.props.onChange}
            />
    }
});


module.exports = Work;
