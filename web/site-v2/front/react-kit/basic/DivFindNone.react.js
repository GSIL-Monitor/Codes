var React = require('react');
var $ = require('jquery');

const DivFindNone = React.createClass({
    render(){
        return(
            <div className="find-none">
                <h3>无数据</h3>
            </div>

        )
    }
});


module.exports = DivFindNone;
