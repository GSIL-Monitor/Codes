var React = require('react');

var Functions = require('../../../../../../../react-kit/util/Functions');
var FormTextarea = require('../FormTextarea.react');

const Note = React.createClass({

    render(){

        return <FormTextarea label='笔记'
                             name='note'
                             value={this.props.data}
                             className='form-input-full'
                             onChange={this.props.onChange}
            />
    }
});


module.exports = Note;
