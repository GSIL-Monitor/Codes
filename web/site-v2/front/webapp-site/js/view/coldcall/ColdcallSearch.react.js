var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ColdcallActions = require('../../action/ColdcallActions');
var ColdcallStore = require('../../store/ColdcallStore');
var CompanySearchInput = require('../../../../react-kit/basic/search/CompanyInput.react');

var Functions = require('../../../../react-kit/util/Functions');

const ColdcallSearch = React.createClass({

    render(){
        var data = this.props.data;
        var matches = data.companies;
        var list = this.props.list;
        var result = data.searchResult;
        return(
            <div>
                <div className="cc-match-hint m-t-10 m-b-5">不是上面的公司？搜搜看库里是否有：</div>

                <CompanySearchInput from="coldcall" />

                <SearchList data={list} result={result} matches={matches}/>
            </div>
        )
    }

});

const SearchList = React.createClass({

    render(){
        if(this.props.data.length == 0 && this.props.result)
            return <div className="cc-search-none">
                        <h4 className="text-red m-t-10">无搜索结果</h4>
                    </div>;

        return(
            <div>
                { this.props.data.map(function (result, index) {
                    return <SearchItem key={index} data={result} matches={this.props.matches}/>;
                }.bind(this))}
            </div>
        )
    }
});

const SearchItem = React.createClass({

    render(){
        var data = this.props.data;
        var roundName = Functions.getRoundName(data.round);
        var link = "../#/company/"+data.code+"/overview";

        var establishDate = data.establishDate;
        if(establishDate != null){
            establishDate = establishDate.substring(0,7);
        }

        var location = data.location;
        if(location != null){
            location = "@"+location;
        }

        var operate=  <a className="a-button right ft-16" onClick={this.add}>
                            <i className="fa fa-plus m-r-5"></i>匹配
                        </a>;

        var matches = this.props.matches;
        var flag = false;
        for(var i in matches){
            if(data.code == matches[i].code){
                flag = true;
            }
        }

        if(flag){
            operate=  <a className="right cc-search-remove" onClick={this.remove}>
                <i className="fa fa-times m-r-5"></i>删除
            </a>
        }
        //target="_blank"

        return(
            <div className="cc-search-item">

                <div className="item-head">
                    <a className="item-name" href={link} >{data.name}</a>
                    <span className="item-round">{roundName}</span>
                    {operate}
                </div>
                <div className="right item-field">
                </div>

                <div className='item-description'>{data.description}</div>
                <div className="item-meta">{establishDate} {location}</div>
            </div>
        )
    },

    add(){
        ColdcallActions.select(this.props.data.code);
    },

    remove(){
        ColdcallActions.remove(this.props.data.code);
    }
});


module.exports = ColdcallSearch;

