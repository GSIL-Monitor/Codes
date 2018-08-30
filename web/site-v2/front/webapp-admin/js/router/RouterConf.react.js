var React = require('react');
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var createHashHistory = require('history/lib/createHashHistory');

var RouterNewDemoDay = require('./demoDay/RouterNewDemoDay.react');
var RouterDemoDayList = require('./demoDay/RouterDemoDayList.react');
var RouterDemoDay = require('./demoDay/RouterDemoDay.react');
var RouterDemoDayPreScores =require('./demoDay/RouterDemoDayPreScores.react');
var RouterDemodaySysCompany = require('./demoDay/RouterDemodaySysCompany');
var RouterOrgList = require('./org/RouterOrgList.react');
var RouterNewOrg = require('./org/RouterNewOrg.react');
var RouterOrgUser = require('./org/RouterOrgUser.react');
var RouterColdCall = require('./coldCall/ColdCall.react.js');
var RouterColdcallDetail = require('../../../webapp-site/js/router/RouterColdcall.react');
var RouterCreateCompany = require('../../../webapp-site/js/router/RouterCreateCompany.react');

var RounterConf= React.createClass({
    render(){
        return(
            <Router history={createHashHistory({ queryKey: false })}>
                <Route path="/"  component={RouterColdCall}/>
                <Route path="/demoday" component={RouterDemoDayList} />
                <Route path="/demoday/:demodayId" component={RouterDemoDay} />
                <Route path="/new/demoday" component={RouterNewDemoDay} />
                <Route path="/demoday/:demodayId/preScores" component={RouterDemoDayPreScores} />
                <Route path="/demoday/:demodayId/sys/company" component={RouterDemodaySysCompany} />

                <Route path="/org" component={RouterOrgList} />
                <Route path="/new/org" component={RouterNewOrg} />
                <Route path="/org/:id/user" component={RouterOrgUser} />

                <Route path="/coldCall" component={RouterColdCall} />
                <Route path="/coldCall/:type" component={RouterColdCall} />
                <Route path="/coldcall/:coldcallId/overview" component={RouterColdcallDetail}/>
                <Route path="/coldcall/:coldcallId/company/create" component={RouterCreateCompany}/>
            </Router>
        )
    }
});


module.exports = RounterConf;