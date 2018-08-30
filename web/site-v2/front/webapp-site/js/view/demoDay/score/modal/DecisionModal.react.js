var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');


var DemoDayActions = require('../../../../action/demoday/DemoDayActions');
var DemoDayStore = require('../../../../store/demoday/DemoDayStore');
var Modal = require('../../../modal/Modal.react');
var Functions = require('../../../../../../react-kit/util/Functions');

var DecisionModal = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var data = state.data;


        return  <Modal id="decision-modal"
                       name="投资决策"
                       type="demodayDecision"
                       data={data}
                />
    }

});


module.exports = DecisionModal;