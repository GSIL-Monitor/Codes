var React = require('react');
var ReactRouter = require('react-router');
var Router = ReactRouter.Router;
var Route = ReactRouter.Route;

var RouterSearch = require('./home/RouterSearch.react');
var RouterCompanyList = require('./home/RouterCompanyList.react.js');
var RouterCompany = require('./RouterCompany.react');
var RouterFunding = require('./RouterFunding.react');
var RouterMember = require('./RouterMember.react');
var RouterMemberNew = require('./member/RouterNew.react');
var RouterMemberUpdate = require('./member/RouterUpdate.react');
var RouterInvestorNew = require('./investor/RouterNew.react');
var RouterInvestorUpdate = require('./investor/RouterUpdate.react');

var RounterConf= React.createClass({
    render(){
        return(
            <Router>
                <Route path="/search" component={RouterSearch} />

                <Route path="/company" >
                    <Route path="list" component={RouterCompanyList} />
                    <Route path="basic/:id" component={RouterCompany} />
                    <Route path="funding/:id" component={RouterFunding} />
                    <Route path="member/:id" component={RouterMember} />
                </Route>
                <Route path="/member">
                    <Route path="new" component={RouterMemberNew} />
                    <Route path="update/:id" component={RouterMemberUpdate} />
                </Route>
                <Route path="/investor">
                    <Route path="new" component={RouterInvestorNew} />
                    <Route path="update/:id" component={RouterInvestorUpdate} />
                </Route>
            </Router>
        )
    }
});


module.exports = RounterConf;