var React = require('react');
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;

var RouterOverview = require('./RouterOverview.react.js');

var RounterConf= React.createClass({
    render(){
        return(
            <Router>
                <Route path="/company/:code/overview" component={RouterOverview} />
            </Router>
        )
    }
});


module.exports = RounterConf;