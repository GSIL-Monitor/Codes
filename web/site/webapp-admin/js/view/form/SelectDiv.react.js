var React = require('react');

var SelectDiv = React.createClass({
    render() {
        return (
            <div className="div-select-list">
                { this.props.select.map(function(result){
                    return  <SelectElement key={result.value}
                                           name={result.name}
                                           value={result.value}
                                           onClick={this.props.onClick}
                            />;
                }.bind(this))}
            </div>
        );
    },

    handleChange(event){
        this.props.onChange(event);
    }
});

var SelectElement = React.createClass({
    render(){
        return(
            <div onClick={this.handleClick} >
                {this.props.name}
            </div>
        )
    },

    handleClick(){
        this.props.onClick(this.props.value);
    }
});

module.exports = SelectDiv;
