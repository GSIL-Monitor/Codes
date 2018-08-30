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
var SelectedFilters = require('./filter/selected/SelectedFilters.react');

const MobileSearchResult = React.createClass({
    render(){
        var data = this.props.data;

        var loading;
        if(data.loading)
            loading = <Loading />;

        if(!data.filterLoad){
            if(data.count == 0){
                return (
                    <div className={this.props.className}>
                        <SearchFilter data={data} />
                        <h3 className="m-t-30 text-center">无搜索结果</h3>
                    </div>
                )
            }
        }

        return (
            <div className={this.props.className}>
                <SearchFilter data={data} />

                <CompanyList data={data.list}/>
                {loading}
            </div>
        )
    }
});



const SearchFilter = React.createClass({
    render(){
        var data = this.props.data;
        if(data.filterLoad)
            return null;

        var count;
        var countNum = Functions.parseCount(data.count);
        count = '找到了 '+countNum+' 个结果';

        return(
            <div className="sort-bar">
                <SelectedFilters data={data}/>
                <span className="result-count m-r-30">{count}</span>
                <a className="a-button ft-16 right" onClick={this.clickFilter}>筛选</a>
            </div>
        )
    },

    clickFilter(){
        $('#search-filter-modal').show();
    }
});


module.exports = MobileSearchResult;