var React = require('react');
var $ = require('jquery');

var SearchActions = require('../../action/SearchActions');
var Functions = require('../../../../react-kit/util/Functions');

const SortBar = React.createClass({
    render(){
        var data = this.props.data;
        if(data.filterLoad)
            return null;

        var sortSelect = Functions.sortSelect();
        var sort = data.sort;
        var sortName;
        for(var i in sortSelect){
            if(sortSelect[i].value == sort){
                sortName = sortSelect[i].name
            }
        }

        var count;
        var countNum = Functions.parseCount(data.count);
        if(data.type == 'latest'){
            count = '当前收录了 '+countNum + ' 个公司';
            return  <div className="sort-bar latest-bar">
                        <span className="result-count">{count}</span>
                        <span className="right ft-13">按系统收录时间排序</span>
                    </div>
        }else{
            count = '找到了 '+countNum+' 个结果';
        }

        return(
            <div>
                <div className="sort-bar">
                    <span className="result-count m-r-30">{count}</span>

                    <button className="btn btn-white btn-menu-select right" onClick={this.toggleClick}>
                        <i>排序: </i>
                        <span className="sort-type">{sortName}</span>
                    </button>
                </div>

                <div className="select-menu-modal" >
                    <div className="select-menu-header" onClick={this.showClick}>
                        <span className="octicon-x right" role="button" onClick={this.hideClick}>×</span>
                        <span className="select-menu-title">排序选择</span>
                    </div>

                    <div className="select-menu-list">
                        { sortSelect.map(function(result){
                            return  <SortSelect  key={result.value}
                                                 data={result}
                                                 sort={sort} />;
                        }.bind(this))}
                    </div>

                </div>
            </div>
        )
    },
    toggleClick(e){
        $('.select-menu-modal').toggle();
        e.stopPropagation();
    },
    showClick(e){
        $('.select-menu-modal').show();
        e.stopPropagation();
    },

    hideClick(e){
        $('.select-menu-modal').hide();
        e.stopPropagation();
    }

});


const SortSelect = React.createClass({
    render(){
        return (
            <span className="select-menu-item" onClick={this.handleClick}>
            <span className="octicon">
                <SortChecked data={this.props.data.value} sort={this.props.sort}/>
            </span>
            <span className="select-menu-item-text">
                {this.props.data.name}
            </span>
         </span>
        )
    },

    handleClick(){
        SearchActions.changeSort(this.props.data.value);
    }
});

const SortChecked = React.createClass({
    render(){
        var sortCheck;
        if (this.props.sort == this.props.data) {
            return(
                <i className="fa fa-check"></i>
            )
        }else{
            return null;
        }

    }
});

module.exports = SortBar;
