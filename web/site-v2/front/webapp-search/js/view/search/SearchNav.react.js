var React = require('react');
var $ = require('jquery');

var SearchInput = require('../../../../react-kit/basic/search/SearchInput.react.js');
var BasicSearchActions = require('../../../../react-kit/action/SearchActions');

const SearchNav = React.createClass({
    render(){
        //<div className="change-search-type"><a>高级搜索</a></div>

        return(
            <div className="search-nav">
                <div className="column one-fourth">
                    <div className="search-type-name">搜索</div>
                </div>
                <div  className="column  three-fourths">
                    <div className="div-search">

                        <SearchInput className="search-input-full"
                                     type={this.props.type}
                                     value={this.props.value}/>

                        <button className="btn btn-white search-btn" onClick={this.clickSearch}>搜索</button>
                    </div>

                </div>
            </div>
        )
    },

    handleChange(e){
        this.props.onChange(e.target.value);
    },

    clickSearch(){
        BasicSearchActions.clickSearch();
    }
});





module.exports = SearchNav;
