var React = require('react');
var Resetpwd = require('../view/Resetpwd.react');

var Footer = require('../../../react-kit/basic/footer/Footer.react.js');

var RouterResetpwd = React.createClass({

    render(){
        var userId = this.props.params.userId;
        var oneTimePwd = this.props.params.oneTimePwd;

        return(
            <Resetpwd userId={userId} oneTimePwd={oneTimePwd}/>
        )
    }
});

module.exports = RouterResetpwd;
