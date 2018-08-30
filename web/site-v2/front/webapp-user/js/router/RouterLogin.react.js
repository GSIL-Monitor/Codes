var React = require('react');
var Login = require('../view/Login.react');

var Footer = require('../../../react-kit/basic/footer/Footer.react.js');

var RouterLogin = React.createClass({

    render(){
        return(
            <Login />
        )
    }
});

module.exports = RouterLogin;
