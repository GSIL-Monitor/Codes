var React = require('react');

var Sidebar = React.createClass({

    handleClick: function(){
    },

    render: function(){
        return(
            <div className="sidebar">
                <ul>
                    <li onClick={this.handleClick}> 公司</li>
                    <li onClick={this.handleClick}> 众筹</li>
                </ul>

            </div>
        );
    }
});


module.exports = Sidebar;