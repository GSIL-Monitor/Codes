var React = require('react');
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var createHashHistory = require('history/lib/createHashHistory');

var RouterLogin = require('./RouterLogin.react');
var RouterForgetpwd = require('./RouterForgetpwd.react');
var RouterResetpwd = require('./RouterResetpwd.react');

var PageNotFound = require('../../../react-kit/error/PageNotFound.react');

var RounterConf= React.createClass({
    render(){
        return(
            <Router history={createHashHistory({ queryKey: false })}>
                <Route path="/login" component={RouterLogin} />
                <Route path="/forgetpwd" component={RouterForgetpwd} />
                <Route path="/resetpwd/:userId/:oneTimePwd" component={RouterResetpwd}/>

                <Route path="*" component={PageNotFound}/>
            </Router>
        )
    }
});


module.exports = RounterConf;