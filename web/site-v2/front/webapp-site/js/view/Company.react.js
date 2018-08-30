var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Overview = require('./company/Overview.react');
var UserCompany = require('./user/UserCompany.react');

var InitActions = require('../action/InitActions');
var InitStore = require('../store/InitStore');
var Functions = require('../../../react-kit/util/Functions');


const Company = React.createClass({

    mixins: [Reflux.connect(InitStore, 'data')],

    componentWillMount() {
        InitActions.initCompany(this.props.code);
    },

    componentWillReceiveProps(nextProps) {
        InitActions.initCompany(nextProps.code);
    },


    render(){

        if(Functions.isEmptyObject(this.state))
            return null;

        var code = this.state.data.code;

        return (
            <div className="main-body">
                <div className="column three-fourths left-block">
                    <Overview code={code}/>
                </div>

                <div className="column one-fourth user-part">
                    <UserCompany code={code} />
                </div>

            </div>

        );
    }


});







module.exports = Company;

