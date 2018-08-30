var React = require('react');

var HeaderNav = React.createClass({

    render(){
        //href="/#"
        return(
            <div className="header-logo left m-r-30">
                <h3><a >烯牛数据</a></h3>
            </div>
        )
    }

});


module.exports = HeaderNav;