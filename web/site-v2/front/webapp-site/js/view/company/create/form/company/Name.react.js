var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var FormInput = require('../FormInput.react');

const Name = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render(){
        var hint;
        var className = 'form-input-short';
        if(!Functions.isEmptyObject(this.state)){
            var data = this.state.validate;
            var validate = data.name;
            if(!Functions.isEmptyObject(validate)){
                if(validate.show)
                    hint = <span className="text-red">{validate.hint}</span>;
                if(!validate.validation){
                    className += ' error';
                }
                else if(validate.show&&validate.hint=='usable'){
                    hint = <span className="cc-text-green"><i className="fa fa-check"></i></span>;
                }
            }

            var searchList = data.searchList;
        }

        return <div>
                    <FormInput label='产品名称'
                              name='name'
                              required={true}
                              value={this.props.data}
                              className= {className}
                              onChange={this.change}
                              onBlur={this.blur}
                              hint= {hint}
                              id={this.props.id}
                    />
                    <SearchHint data={searchList}/>

               </div>
    },

    change(e){
        ValidateActions.change(e.target.name);
        this.props.onChange(e);
    },

    blur(e){
        ValidateActions.name(e.target.value);
    }

});



const SearchHint = React.createClass({
    render(){
        var searchList = this.props.data;
        if(searchList == null) return null;
        if(searchList.length == 0) return null;

        return <div className="company-search-hint">
                    <div className="cc-form-left cc-search-hint">你可能在找这些公司？</div>
                    <div className="cc-form-right cc-search-list">
                        {searchList.map(function(result,index){
                            return <HintItem data={result} key={index}/>
                        })}
                    </div>
                </div>
    }
});


const HintItem = React.createClass({
    render(){
        var data = this.props.data;
        var hintName;
        var completion = data.completion[0];
        var name = data.name;
        if(completion == name ){
            hintName = name
        }else{
            hintName = <span>{name} -- {completion} </span>
        }

        var link = './#/company/'+data.code+'/overview';

        return(
            <div><a href={link} target="_blank">{hintName}</a></div>
        )
    }
});


module.exports = Name;