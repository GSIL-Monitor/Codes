var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SearchStore = require('../../store/SearchStore');
var SearchActions = require('../../action/SearchActions');
var SortBar = require('./SortBar.react');

var Functions = require('../../../../react-kit/util/Functions');
var ButtonLoadMore = require('../../../../react-kit/basic/ButtonLoadMore.react');
var CompanyList = require('../../../../react-kit/company/CompanyList.react');
var Loading = require('../../../../react-kit/basic/Loading.react');

const SearchResult = React.createClass({
    render(){
        var data = this.props.data;

        var loading;
        if(data.loading)
            loading = <Loading />;


        if(!data.filterLoad){
            if(data.count == 0){
                return (
                    <div className={this.props.className}>
                        <h3 className="m-t-30 text-center">无搜索结果</h3>
                    </div>
                )
            }
        }

        return (
            <div className={this.props.className}>
                <SortBar data={data} />

                <CompanyList data={data.list}/>
                {loading}
            </div>
        )
    }
});



const CreateCompany = React.createClass({
    render(){
        return (
            <div className="m-t-20 text-center">
                <a className="ft-18 a-add " href="/#/company/create">
                    <i className="fa fa-plus m-r-10"></i>新建公司
                </a>
            </div>
        )
    }
});

module.exports = SearchResult;