var React = require('react');
var $ = require('jquery');


var Functions = require('../../../../react-kit/util/Functions');

const SortBar = React.createClass({
    render(){
        var sortSelect =  Functions.sortSelect();
        var sort = this.props.sort;
        var sortName;
        for(var i in sortSelect){
            if(sortSelect[i].value == sort){
                sortName = sortSelect[i].name
            }
        }

        return(
            <div>
                <div className="sort-bar">
                    <span className="result-count">找到了{this.props.count}个结果</span>
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
                            return  <SortSelect  key={result.value}  data={result} sort={sort} />;
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
        this.props.onSortChange(this.props.data.value);
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
