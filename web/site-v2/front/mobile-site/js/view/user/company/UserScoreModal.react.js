var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var UserCompanyStore = require('../../../../../webapp-site/js/store/UserCompanyStore');
var UserCompanyActions = require('../../../../../webapp-site/js/action/UserCompanyActions');
var Modal = require('../../modal/Modal.react');
var Functions = require('../../../../../react-kit/util/Functions');

var UserScoreModal = React.createClass({

    mixins: [Reflux.connect(UserCompanyStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var data = state.data;

        return  <Modal id="user-score-modal"
                       name="评分"
                       type="userScore"
                       data = {data}
                />
    }

});


module.exports = UserScoreModal;