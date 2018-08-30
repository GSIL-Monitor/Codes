var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../../modal/Modal.react');
var Functions = require('../../../../../../react-kit/util/Functions');
var RecruitStore = require('../../../../store/company/RecruitStore');

var JobModal = React.createClass({

    mixins: [Reflux.connect(RecruitStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        return  <Modal id="job-modal"
                       name="职位详细信息"
                       type="job"
                       data= {state.data.selected}
                />
    }

});


module.exports = JobModal;