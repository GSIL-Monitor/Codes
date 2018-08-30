var React = require('react');
var ReactPropTypes = React.PropTypes;
var Required = require('../util/Required')
var Textarea = React.createClass({

    //propTypes: {
    //    className: ReactPropTypes.string,
    //    id: ReactPropTypes.string,
    //    name: ReactPropTypes.string,
    //    value: ReactPropTypes.string,
    //    placeholder: ReactPropTypes.string
    //},

    getInitialState: function () {
        return {
            name: this.props.value || ''
        };
    },

    render: function () {
        //console.log(this.props.name + ":" + this.props.value);
        if(this.props.required){
            return (
                <textarea
                    className={this.props.className}
                    id = {this.props.id}
                    name = {this.props.name}
                    value={this.props.value}
                    onChange={this.handleChange}
                    onBlur={this.handleBlur}
                    onMouseOver={this.onMouseOver}
                    onMouseOut={this.onMouseOut}
                    />
            );
        }
        else{
            return (
                <textarea
                    className={this.props.className}
                    id = {this.props.id}
                    name = {this.props.name}
                    value={this.props.value}
                    onChange={this.handleChange}
                    onMouseOver={this.onMouseOver}
                    onMouseOut={this.onMouseOut}
                    />
            );
        }

    },

    handleChange: function (event) {
        this.props.onChange(event);
    },

    handleBlur(event){
        Required.handleBlur(event)
    },

    onMouseOver(){
        //document.body.style.overflow = 'hidden';
    },

    onMouseOut(){
        //document.body.style.overflow = 'auto';
    }
});

module.exports = Textarea;
