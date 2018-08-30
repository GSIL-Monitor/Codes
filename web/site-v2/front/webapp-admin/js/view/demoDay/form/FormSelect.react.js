var React = require('react');

var FormSelect = React.createClass({

    render() {
        return (
            <select className={this.props.className}
                    name={this.props.name}
                    value={this.props.value}
                    onChange={this.handleChange}>

                {this.props.select.map(function (result, index) {
                    return <Option key={index} name={result.name} value={result.value}/>;
                }.bind(this))}

            </select>
        );
    },

    handleChange(e){
        this.props.onChange(e);
    }
});

var Option = React.createClass({
    render(){
        return (
            <option value={this.props.value}>
                {this.props.name}
            </option>
        )
    }
});

module.exports = FormSelect;
