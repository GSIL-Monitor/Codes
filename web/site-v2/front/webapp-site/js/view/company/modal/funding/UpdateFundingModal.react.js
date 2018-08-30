var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var FormSelect = require('../../../../../../react-kit/form/FormSelect.react');
var FormInput = require('../../../../../../react-kit/form/FormInput.react');
var Functions = require('../../../../../../react-kit/util/Functions');
var AddFundingInvestor = require('./investor/AddFundingInvestor.react.js');


var CompanyStore = require('../../../../store/CompanyStore');
var CompanyActions = require('../../../../action/CompanyActions');

var Modal = require('../../../modal/Modal.react');

var UpdateFundingModal = React.createClass({

    mixins: [Reflux.connect(CompanyStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var funding = state.data.selectedFunding;
        //var funding = state.data.cloneSelectedFunding;

        return(
            <Modal id="update-funding-modal"
                   name="更新融资事件"
                   type="updateFunding"
                   comfirmName="更新"
                   data={funding}
                />
        )


        //return <Funding id="update-funding-modal" name="更新融资事件" comfirmName="更新" data={funding}/>

    }

});



module.exports = UpdateFundingModal;