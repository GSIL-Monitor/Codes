var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../../../../../webapp-site/js/action/demoday/DemoDayActions');
var DemoDayStore = require('../../../../../../webapp-site/js/store/demoday/DemoDayStore');
var Modal = require('../../../modal/Modal.react');
var Functions = require('../../../../../../react-kit/util/Functions');

var ScoreModal = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var data = state.data;

        return  <Modal id="demoday-score-modal"
                       name="项目打分"
                       type="demodayScore"
                       data = {data}
            />
    }

});


module.exports = ScoreModal;