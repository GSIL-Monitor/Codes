var React = require('react');

const PageNotFound = React.createClass({
    render(){
        return(
            <div className="main-body">
                <div className="load-fail" onClick={this.home}>
                    页面未找到, 回到主页
                </div>
            </div>
        )
    },
    home(){
        window.location.href= "/#/";
    }
});

module.exports = PageNotFound;

