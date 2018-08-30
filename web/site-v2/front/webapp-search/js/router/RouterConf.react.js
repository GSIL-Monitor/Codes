var React = require('react');
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var createHashHistory = require('history/lib/createHashHistory');

var RouterSearch = require('./RouterSearch.react');
var PageNotFound = require('../../../react-kit/error/PageNotFound.react');

var RounterConf= React.createClass({
    render(){
        return(
            <Router history={createHashHistory({ queryKey: false })}>
                <Route path="/" component={RouterSearch} />
                <Route path="/:type/" component={RouterSearch} />
                <Route path="/:type/:value" component={RouterSearch} />

                <Route path="*" component={PageNotFound} />

            </Router>
        )
    }
});


module.exports = RounterConf;