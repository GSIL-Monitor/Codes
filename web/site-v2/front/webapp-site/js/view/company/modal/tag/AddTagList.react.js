var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyActions = require('../../../../action/CompanyActions');
var CreateCompanyActions = require('../../../../action/CreateCompanyActions');
var Functions = require('../../../../../../react-kit/util/Functions');
var TagInput = require('../../../../../../react-kit/basic/search/TagInput.react');

const AddTagList = React.createClass({

    render(){

        var tags = this.props.data;
        var from;
        if(this.props.from){
            from=this.props.from;
        }
        if(Functions.isNull(tags)) return null;

        var tagList;
        if(tags.length > 0){
            tagList = tags.map(function(result, index){
                return <TagItem key={index} data={result}  from={from}/>
            })
        }

        return(
            <div>
                {tagList}
            </div>
        )
    }
});


const TagItem = React.createClass({
    render(){
        return(
            <div className="label tag add-item">
                {this.props.data.name}
                <i className="fa fa-times m-l-10 label-close" onClick={this.delete}></i>
            </div>
        )
    },

    delete(){
        if(this.props.from=='createCompany'){
            CreateCompanyActions.deleteNewTag(this.props.data.id);
        }else{
            CompanyActions.deleteNewTag(this.props.data.id);
        }

    }
});


module.exports = AddTagList;