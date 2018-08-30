var React = require('react');
var $ = require('jquery');


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
                        <input type="text" className="search-input-full" value={this.props.value}
                               onKeyDown={this.handleChange}/>
                        <button className="btn btn-white search-btn">搜索</button>
                    </div>
                    <div className="div-search-meta">
                        <span>其他人还看了</span>
                        <a className="relate-search">汽车后服务</a>

                    </div>
                </div>
            </div>
        )
    },

    handleChange(e){
        console.log(e);

        this.props.onChange(e.target.name, e.target.value);
    }
});



module.exports = SearchNav;
