var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompsActions = require('../../../../action/company/CompsActions');
var Functions = require('../../../../../../react-kit/util/Functions');
var SearchCompanyStore = require('../../../../../../react-kit/store/SearchCompanyStore');

const AddCompsList = React.createClass({

    mixins: [Reflux.connect(SearchCompanyStore, 'searchMatch')],

    render(){

        var searchMatches = [];
        var matchList;
        if(!Functions.isEmptyObject(this.state)){
            searchMatches = this.state.searchMatch.matches;
        }

        var newList = this.props.data;
        var type = this.props.type;
        if(Functions.isNull(type)){
            type = 'list';
        }

        if(newList.length > 0){
            matchList = newList.map(function(result, index){
                return <CompanyItem key={index} id={index} data={result} type={type} />
            })
        }

        return(
            <div>
                {matchList}
            </div>
        )
    }
});


const CompanyItem = React.createClass({
    render(){

        var data = this.props.data;
        var descClass = "item-description add-item-desc";

        var roundName = Functions.getRoundName(data.company.round);
        var link = "../#/company/"+data.company.code+"/overview";

        var establishDate = data.company.establishDate;
        if(establishDate != null){
            establishDate = establishDate.substring(0,7);
        }

        var location = data.location;
        if(location != null){
            location = "@"+location;
        }

        var comps_brief= data.company.brief;
        var brief;
        if(!Functions.isNull(comps_brief)){
            brief = <div className="comps-brief">{comps_brief}</div>
        }

        if(this.props.type == 'modal'){
            return(
                <div className="label tag add-item">
                    <a href={link} target='_blank'>{this.props.data.company.name}</a>
                    <i className="fa fa-times m-l-10 label-close" onClick={this.delete}></i>
                </div>
            )
        }

        return(
            <div className="comps-list-item update-comps-item add-item" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                <div className="comps-close">
                    <i className="fa fa-times fa-lg label-close right" onClick={this.delete}></i>
                </div>
                <div className="item-head">
                    <div className="left m-r-10">
                        <a className="comps-name add-comps-name" href={link} target="_blank" >{data.company.name}</a>
                    </div>
                    <div className="left m-r-10">{roundName}</div>
                    {brief}
                </div>

                <div className={descClass}>{data.company.description}</div>
                <div>{establishDate} {location}</div>
            </div>
        )

    },

    delete(){
        CompsActions.deleteNew(this.props.id);
    }
});


module.exports = AddCompsList;