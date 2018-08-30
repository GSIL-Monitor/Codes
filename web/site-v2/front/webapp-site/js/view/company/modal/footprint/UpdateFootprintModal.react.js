var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var FormSelect = require('../../../../../../react-kit/form/FormSelect.react');
var FormInput = require('../../../../../../react-kit/form/FormInput.react');
var Functions = require('../../../../../../react-kit/util/Functions');

var CompanyStore = require('../../../../store/CompanyStore');
var CompanyActions = require('../../../../action/CompanyActions');

var Modal = require('../../../modal/Modal.react');

var UpdateFootprintModal = React.createClass({

    mixins: [Reflux.connect(CompanyStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var footprint = state.data.selectedFootprint;

        return(
            <Modal id="update-footprint-modal"
                   name="更新发展足迹"
                   type="updateFootprint"
                   comfirmName="更新"
                   data={footprint}
                />
        )

    }

});



module.exports = UpdateFootprintModal;