var React = require('react');

var Select = React.createClass({
    render() {
        return (
            <select name={this.props.name} value={this.props.value} onChange={this.handleChange}>
                { this.props.select.map(function(result){
                    return  <Option key={result.value} name={result.name} value={result.value} />;
                }.bind(this))}
            </select>
        );
    },

    handleChange(event){
        this.props.onChange(event);
    }
});

var Option = React.createClass({
    render(){
        return(
            <option value={this.props.value}>
                {this.props.name}
            </option>
        )
    }
});

module.exports = Select;
