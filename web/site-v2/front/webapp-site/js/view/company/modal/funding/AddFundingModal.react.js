var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../../modal/Modal.react');
var Functions = require('../../../../../../react-kit/util/Functions');

var CompanyStore = require('../../../../store/CompanyStore');
var CompanyActions = require('../../../../action/CompanyActions');

var AddFundingModal = React.createClass({

    mixins: [Reflux.connect(CompanyStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        return(
            <Modal id="add-funding-modal"
                   name="添加融资事件"
                   type="addFunding"
                   comfirmName="添加"
                   data={state.data.addFunding}
                    />
        )
    }

});



module.exports = AddFundingModal;