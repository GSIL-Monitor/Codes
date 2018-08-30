/**
 * Created by haiming on 16/2/3.
 */
var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../../../react-kit/util/Functions');
var FormTextarea = require('../FormTextarea.react');

const Description = React.createClass({


    render(){

        return <FormTextarea label='项目介绍'
                          name='description'
                          value={this.props.data}
                          className='form-input-full'
                          onChange={this.props.onChange}
            />
    }
});


module.exports = Description;
