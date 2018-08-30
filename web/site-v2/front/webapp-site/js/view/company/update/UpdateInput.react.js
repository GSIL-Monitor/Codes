var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var Functions = require('../../../../../react-kit/util/Functions');


const UpdateInput = React.createClass({
    render(){
        if(this.props.onBlur == null){
            return   <input  className={this.props.className}
                             name={this.props.name}
                             value={this.props.data}
                             placeholder={this.props.placeholder}
                             onChange={this.change}
                             ref = {this.props.name}
                        />
        }

        return(
            <input  className={this.props.className}
                    name={this.props.name}
                    value={this.props.data}
                    placeholder={this.props.placeholder}
                    onChange={this.change}
                    onBlur={this.blur}
                    ref = {this.props.name}
                />
        )
    },

    change(e){
        var name = e.target.name;
        var value = e.target.value;
        if(name == 'investment'){
            CompanyActions.changeInvestment(value);
        }else if(name == "shareRatio"){
            CompanyActions.changeShareRatio(value);
        }else if(name == 'preMoney' || name == 'postMoney'){
            CompanyActions.changeMoney(name, value);
        }

        else{
            CompanyActions.changeCompany(name, value);
        }
    },

    blur(e){
        this.props.onBlur(e.target.value);
    }
});


module.exports = UpdateInput;