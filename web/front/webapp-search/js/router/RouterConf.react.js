var React = require('react');
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;

var RouterSearch = require('./RouterSearch.react');

var RounterConf= React.createClass({
    render(){
        return(
            <Router>
                <Route path="/search" component={RouterSearch} />
            </Router>
        )
    }
});


module.exports = RounterConf;