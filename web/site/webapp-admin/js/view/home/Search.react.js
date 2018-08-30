var React = require('react');
var $ = require('jquery');

var SearchStore = require('../../store/home/SearchStore');
var SearchAction = require('../../action/home/SearchAction');

var SelectDiv = require('../form/SelectDiv.react');
var Functions = require('../../util/Functions');

const Search = React.createClass({

    componentDidMount() {
        var data={ids: '881,882,883'};

        SearchAction.get(data.ids);
        SearchStore.addChangeListener(this._onChange);
    },

    componentWillUnmount(){
        SearchStore.removeChangeListener(this._onChange);
    },


    render() {

        var state = this.state;
        if(state == null){
            return null;
        }
        else if(state.list.length == 1){
            return(
                <div>
                    <SearchResult />
                </div>
            )
        }
        else{
            return (
                <div>
                    <SearchNav />

                    <SearchAside />
                    <SearchResult data = {this.state.list} className="column three-fourths"/>
                </div>
            );
        }
    },

    _onChange(){
        this.setState({list:SearchStore.get()})
    }
});

const SearchNav = React.createClass({
    render(){
        return(
            <div className="search-nav">
                <div className="column one-fourth">
                    <div className="search-type-name">搜索</div>
                    <div className="change-search-type"><a>高级搜索</a></div>
                </div>
                <div  className="column  three-fourths">
                    <div className="div-search">
                        <input type="text" className="search-input-full" value="" />
                        <button className="btn btn-white search-btn">搜索</button>
                    </div>
                    <div className="div-search-meta">
                        <span>其他人还看了</span>
                        <a className="relate-search">汽车后服务</a>

                        <div className="right search-count">

                        </div>
                    </div>
                </div>
            </div>
        )
    }
});



const SearchAside = React.createClass({
    render(){
        return(
            <div className="column  one-fourth">
               <div className="m-t-20 m-r-20">
                    <SearchType />
                    <Filter />
               </div>
            </div>
        )
    }
});


const SearchType = React.createClass({
    render(){
        return(
            <nav className="menu">
                <a className="menu-item selected">
                    <span className="octicon">
                        <i className="fa fa-building"></i>
                    </span>
                    公司
                    <span className="counter">3,981</span>
                </a>
                <a className="menu-item ">
                    <span className="octicon">
                        <i className="fa fa-tag"></i>
                    </span>
                    关键字
                    <span className="counter">482,316</span>
                </a>

                <a className="menu-item ">
                    <span className="octicon">
                        <i className="fa fa-newspaper-o"></i>
                    </span>
                    新闻
                    <span className="counter">416</span>
                </a>



                <a  className="menu-item ">
                    <span className="octicon">
                        <i className="fa fa-briefcase"></i>
                    </span>
                    投资人
                    <span className="counter">12,836</span>
                </a>
                <a className="menu-item ">
                    <span className="octicon">
                        <i className="fa fa-users"></i>
                    </span>
                    创业者
                    <span className="counter">45</span>
                </a>
            </nav>
        )
    }
});


const Filter = React.createClass({

    render(){
        var roundSelect = Functions.roundSelect();

        return(
            <div>
                <h4 className="filter-head">融资轮次</h4>
                <SelectDiv select={roundSelect} />

                <div className="more-filter">
                    <a>更多过滤</a>
                </div>
            </div>
        )
    }
});



const SearchResult = React.createClass({
    render(){
        return (
            <div className={this.props.className}>
                <SortBar count={this.props.data.length}/>

                <div>
                    { this.props.data.map(function (result) {
                        return <Element key={result.id} data={result}/>;
                    }.bind(this))}

                </div>
            </div>
        )
    }
});




const SortBar = React.createClass({
    render(){
        var sortSelect =  Functions.sortSelect();
        var sort = SearchStore.getSort();
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
                            return  <SortSelect  key={result.value}  data={result} />;
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
                <SortChecked data={this.props.data.value}/>
            </span>
            <span className="select-menu-item-text">
                {this.props.data.name}
            </span>
         </span>
        )
    },

    handleClick(){
        SearchAction.changeSort(this.props.data.value);
    }
});

const SortChecked = React.createClass({
    render(){
        var sortCheck;
        if (SearchStore.getSort() == this.props.data) {
            return(
                <i className="fa fa-check"></i>
            )
        }else{
            return null;
        }



    }
});


const Element = React.createClass({
    render(){
        var data = this.props.data;
        var descClass = "item-description ";
        if (this.state != null){
            if(this.state.selected)
                descClass = descClass+"auto-height";
        }

        var roundName = Functions.getRoundName(data.round);
        var link = "#/company/basic/"+data.id;

        return(
            <div className="search-list-item" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                <div className="right item-field">
                    Saas
                </div>
                <div className="item-head">
                    <a className="item-name" href={link} target="_blank">{data.name}</a>
                    <span className="m-l-10 m-r-20">{roundName}</span>
                    <span className="tag">
                        团队
                    </span>
                    <span className="tag">
                        团队
                    </span>
                    <span className="tag">
                        团队
                    </span>

                </div>
                <div className={descClass}>{data.description}</div>
                <div className="item-meta">{data.establishDate}  @{data.location}</div>
            </div>
        )
    },

    onMouseOver(){
        this.setState({selected: true})
    },

    onMouseOut(){
        this.setState({selected: false})
    }

});



module.exports = Search;

