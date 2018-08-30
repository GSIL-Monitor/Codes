var React = require('react');
var ReactPropTypes = React.PropTypes;

var Select = require('./Select.react');

var FormSelect = React.createClass({

    //propTypes: {
    //    label: ReactPropTypes.string,
    //    name:ReactPropTypes.string,
    //    select: ReactPropTypes.array
    //},

    render: function() {
        //var required = this.props.required?'required':'nonessential';
        //var checkContent;
        //if(this.props.required){
        //    checkContent = <div className={this.props.name+"-required"}>
        //        <span className="required-content m-l-5"><i className="fa fa-times-circle"/>请选择</span>
        //    </div>
        //}
        //else{
        //    checkContent=null;
        //}
        //<span className={required}>*</span>
        //{checkContent}
        return (

            <div className="form-part">
                <label className={this.props.labelClass}>

                    <span>{this.props.label}</span>
                </label>
                <Select id={this.props.id}
                        name={this.props.name}
                        value={this.props.value}
                        select={this.props.select}
                        onChange={this.props.onChange}
                    />
            </div>
        );
    }
});

module.exports = FormSelect;
