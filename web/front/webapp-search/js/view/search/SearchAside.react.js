var React = require('react');
var $ = require('jquery');

var SelectDiv = require('../../../../react-kit/basic/SelectDiv.react');
var Functions = require('../../../../react-kit/util/Functions');


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


module.exports = SearchAside;
