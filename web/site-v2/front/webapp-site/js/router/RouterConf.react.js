var React = require('react');
var $ = require('jquery');
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;
var createHashHistory = require('history/lib/createHashHistory');


var RouterTask = require('./home/RouterTask.react');
var RouterPublish = require('./home/RouterPublish.react');
var RouterDiscovery = require('./home/RouterDiscovery.react');


var RouterCompany = require('./RouterCompany.react.js');
var RouterCreateCompany = require('./RouterCreateCompany.react.js');
var RouterColdcall = require('./RouterColdcall.react.js');

var Setting = require('../view/user/setting/Setting.react');

var RouterRecommendation = require('./RouterRecommedation.react');

var RouterDemoDayList = require('./demoDay/RouterDemoDayList.react');
var RouterDemoDay = require('./demoDay/RouterDemoDay.react');
var RouterCompleteCompany = require('./demoDay/RouterCompleteCompany.react');
var RouterCompanyScore = require('./demoDay/RouterCompanyScore.react');

var RouterNews = require('./RouterNews.react');

var RouterCollection = require('./collection/RouterCollection.react');
var RouterCollectionDetail = require('./collection/RouterCollectionDetail.react');
var RouterNewCollection = require('./collection/RouterNewCollection.react');

/**** error *****/
var PageNotFound = require('../../../react-kit/error/PageNotFound.react');

var Pics = require('../view/company/product/Pics.react');

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
                <Route path="/demoday" component={RouterDemoDayList} />

                <Route path="/coldcall/:coldcallId/overview" component={RouterColdcall}/>
                <Route path="/coldcall/:coldcallId/company/create" component={RouterCreateCompany}/>
                <Route path="/company/create" component={RouterCreateCompany}/>

                <Route path="/company/:code/overview" component={RouterCompany}/>
                <Route path="/news/:companyId/:newsId" component={RouterNews}/>

                <Route path="/demoday/:id" component={RouterDemoDay} />
                <Route path="/demoday/:id/add/:code" component={RouterCompleteCompany} />
                <Route path="/demoday/:id/company/:code/:type" component={RouterCompanyScore}/>
                <Route path="/demoday/:demodayId/create" component={RouterCreateCompany}/>

                <Route path="/collection" component={RouterCollection} />
                <Route path="/collection/:collectionId" component={RouterCollectionDetail} />
                <Route path="/new/collection" component={RouterNewCollection} />

                <Route path="/setting" component={Setting} />

                <Route path="/pics" component={Pics} />

                <Route path="/404" component={PageNotFound} />
                <Route path="*" component={PageNotFound}/>




            </Router>
        )
    }
});


module.exports = RounterConf;