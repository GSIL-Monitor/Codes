var React = require('react');
var ReactPropTypes = React.PropTypes;

var InputText = require('./InputText.react');

var FormInput = React.createClass({

    //propTypes: {
    //    label: ReactPropTypes.string,
    //    className: ReactPropTypes.string,
    //    id: ReactPropTypes.string,
    //    name:ReactPropTypes.string,
    //    value: ReactPropTypes.string,
    //    placeholder: ReactPropTypes.string
    //},

    render: function () {
        //var required = this.props.required ? 'required' : 'nonessential';
        //var checkContent;
        //var checkedResult;
        //if (this.props.onBlur && (this.props.validate) && (this.props.id == 'name' || this.props.id == 'fullName')) {
        //    checkedResult = <div className={this.props.id+"-checked"}>
        //        <span className="required-content m-l-5"><i className="fa fa-times-circle"/>名称已存在</span>
        //    </div>
        //}
        //else{
        //    checkedResult=null;
        //}
        //if (this.props.required) {
        //    checkContent = <div>
        //        <div className={this.props.name+"-required"}>
        //            <span className="required-content m-l-5"><i className="fa fa-times-circle"/>必填</span>
        //        </div>
        //
        //    </div>
        //}
        //else {
        //    checkContent = null;
        //}
        //<span className={required}>*</span>
        //{checkContent}
        //{checkedResult}
        var unit;
        if(this.props.unit){
           unit= <span className="text-red right funding-unit">（单位:万）</span>;
        }
        return (
            <div className="form-part ">
                <label className={this.props.labelClass}>

                    <span>{this.props.label}</span>
                </label>
                <InputText id={this.props.id}
                           name={this.props.name}
                           value={this.props.value}
                           placeholder={this.props.placeholder}
                           className={this.props.className}
                           onChange={this.props.onChange}
                           onBlur={this.props.onBlur}
                    />
                {unit}
            </div>
        );
    }
    //handleBlur(event){
    //    $('.' + event.target.id + '-validating').show();
    //    this.props.onBlur(event);
    //}
});

module.exports = FormInput;
