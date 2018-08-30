/**
 * Created by haiming on 16/2/3.
 */
var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../../../react-kit/util/Functions');
var FormInput = require('../FormInput.react');

const Founder = React.createClass({
    render(){

        return <FormInput label='创始人姓名'
                          name='name'
                          value={this.props.data}
                          className='form-input-short'
                          onChange={this.props.onChange}
            />
    }

});


module.exports = Founder;
