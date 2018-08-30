var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanySearchInput = require('../../../../../react-kit/basic/search/CompanyInput.react');
var Functions = require('../../../../../react-kit/util/Functions');

const AddSearch = React.createClass({

    render(){
        var data = this.props.data;
        var list = this.props.list;
        var companies = this.props.companies;
        var result = data.searchResult;

        return(
            <div className="m-t-10">

                <div className="dd-submit-hint">请在【下方搜索栏】查找项目/产品/公司名以提交</div>

                <CompanySearchInput from="demoday" demodayId={data.id}/>

                <SearchList data={list} result={result}  companies={companies} id={data.id}/>

            </div>
        )
    }

});

const SearchList = React.createClass({

    render(){
        if(this.props.data.length == 0 && this.props.result)
            return <div className="all-block">
                <h4 className="text-red m-t-10">无搜索结果</h4>
            </div>;

        return(
            <div>
                { this.props.data.map(function (result, index) {
                    return <SearchItem key={index}
                                       data={result}
                                       companies={this.props.companies}
                                       id={this.props.id} />;
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

        var operate;

            //<a className="a-button right" onClick={this.add}>
            //    <i className="fa fa-plus m-r-5"></i> 提交
            //</a>;

        var companies = this.props.companies;
        var flag = false;
        for(var i in companies){
            if(data.code == companies[i].code){
                flag = true;
            }
        }

        if(flag){
            operate = <span className="right ">已提交</span>
        }

        return(
            <div className="cc-search-item">

                <div className="item-head">
                    <a className="item-name" onClick={this.add}>{data.name}</a>
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
        window.location.href = '/#/demoday/'+this.props.id+'/add/'+this.props.data.code;
    }

});


module.exports = AddSearch;

