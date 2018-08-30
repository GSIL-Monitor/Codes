var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyActions = require('../../../../action/CompanyActions');
var Functions = require('../../../../../../react-kit/util/Functions');
var TagInput = require('../../../../../../react-kit/basic/search/TagInput.react');

const AddTagList = React.createClass({

    render(){
        var data = this.props.data;
        var list;
        if(data.length > 0){
            list = data.map(function(result, index){
                return <FootprintItem key={index} data={result} index={index} />
            })
        }

        return(
            <div>
                {list}
            </div>
        )
    }
});


const FootprintItem = React.createClass({
    render(){
        var data = this.props.data;
        return(
            <div className="label label-develop add-item" onClick={this.select}>
                <span>{data.footDate}</span>
                <span className="m-l-10">{data.description}</span>
                <i className="fa fa-times m-l-10 label-close right" onClick={this.delete}></i>
            </div>
        )
    },

    delete(){
        CompanyActions.deleteNewFootprint(this.props.index);
    }
});


module.exports = AddTagList;