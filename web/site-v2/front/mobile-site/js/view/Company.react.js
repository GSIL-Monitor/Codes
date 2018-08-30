var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Overview = require('./company/Overview.react');
var UserCompany = require('./user/company/UserCompany.react.js');

var InitActions = require('../../../webapp-site/js/action/InitActions');
var InitStore = require('../../../webapp-site/js/store/InitStore');
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
            <div>
                <Overview code={code}/>
                <UserCompany code={code} />
            </div>

        );
    }


});


module.exports = Company;

