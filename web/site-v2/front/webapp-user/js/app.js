var ReactDOM = require('react-dom');
var React = require('react');
var RouterConf = require('./router/RouterConf.react');

var APP= React.createClass({

    render(){
        return(
            <div>
                <div className="page-wrapper">
                    <RouterConf />
                </div>

            </div>
        )
    }

});

ReactDOM.render(
    <APP />,
    document.getElementById('app')
);











