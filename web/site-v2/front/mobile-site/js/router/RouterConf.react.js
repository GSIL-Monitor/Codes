var React = require('react');
var $ = require('jquery');
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var createHashHistory = require('history/lib/createHashHistory');

var RouterTask = require('./home/RouterTask.react');
var RouterPublish = require('./home/RouterPublish.react');
var RouterDiscovery = require('./home/RouterDiscovery.react');

var RouterRecommendation = require('./RouterRecommedation.react');

var RouterCompany = require('./company/RouterCompany.react');
var RouterNews = require('./company/RouterNews.react');

var RouterColdcall = require('./RouterColdcall.react');

var RouterDemodayList = require('../../../webapp-site/js/router/demoDay/RouterDemoDayList.react');
var RouterDemoday = require('./demoday/RouterDemoday.react');
var RouterCompanyScore = require('./demoday/RouterCompanyScore.react');
var RouterCompanyDecision = require('./demoday/RouterCompanyDecision.react');

var RouterSearch = require('./RouterSearch.react');

var Setting = require('../../../webapp-site/js/view/user/setting/Setting.react');

const RounterConf = React.createClass({

    render(){
        return(
            <Router history={createHashHistory({ queryKey: false })}>
                <Route path="/" component={RouterTask}/>
                <Route path="/task" component={RouterTask}/>
                <Route path="/task/:type/:status" component={RouterTask}/>
                <Route path="/publish" component={RouterPublish}/>
                <Route path="/publish/:status" component={RouterPublish}/>
                <Route path="/discovery" component={RouterDiscovery}/>
                <Route path="/discovery/:status" component={RouterDiscovery}/>

                <Route path="/recommendation" component={RouterRecommendation} />
                <Route path="/demoday" component={RouterDemodayList}/>

                <Route path="/company/:code/overview" component={RouterCompany}/>
                <Route path="/news/:companyId/:newsId" component={RouterNews}/>

                <Route path="/coldcall/:coldcallId/overview" component={RouterColdcall}/>

                <Route path="/demoday/:id" component={RouterDemoday}/>
                <Route path="/demoday/:id/company/:code/:type" component={RouterCompanyScore}/>
                <Route path="/demoday/:id/company/:code/:type/decision" component={RouterCompanyDecision}/>

                <Route path="/search/open" component={RouterSearch}/>
                <Route path="/search/open/:value" component={RouterSearch}/>

                <Route path="/setting" component={Setting} />

            </Router>
        )
    }
});


module.exports = RounterConf;