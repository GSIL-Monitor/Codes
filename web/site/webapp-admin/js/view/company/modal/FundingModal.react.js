var React = require('react');
var Modal = require('../../modal/Modal.react.js');


var FundingAction = require('../../../action/FundingAction');
var FundingStore = require('../../../store/FundingStore');

var FundingModal = React.createClass({
    render(){
        return(
            <div>
                <Modal id="modal-update"
                       name="确认更新"
                       comfirm={this.handleComfirm} />

                <Modal id="modal-reset"
                       name="确认还原"
                       comfirm={this.handleReset} />

                <Modal id="modal-delete"
                       name="融资记录删除"
                       comfirm={this.deleteFunding} />

                <Modal id="modal-add-funding"
                       name="融资记录"
                       content="AddFunding"
                       comfirm={this.addFundingDB}
                       comfirmName="添加"/>

                <Modal id="modal-add-funding-investor"
                       name="投资方"
                       content="AddFundingInvestor"
                       comfirm={this.addFIRDB}
                       comfirmName="添加"/>

                <Modal id="modal-delete-fir"
                       name="相关投资方删除"
                       comfirm={this.deleteFIR} />
            </div>
        )
    },

    handleComfirm(){
        var store = FundingStore.getRound();
        FundingAction.updateFundingDB(store.funding);
    },

    handleReset(){
        FundingAction.resetRound();
    },

    deleteFunding(){
        var store = FundingStore.getRound();
        console.log(store)
        FundingAction.deleteFunding(store.funding);
    },

    deleteFIR(){
        var store = FundingStore.getFIR();
        FundingAction.deleteFIR(store);
    },

    addFundingDB(){
        FundingAction.addFundingDB(FundingStore.getAdd());
    },

    addFIRDB(){
        FundingAction.addFIRDB(FundingStore.getAddFIR());
    }

});



module.exports = FundingModal;
