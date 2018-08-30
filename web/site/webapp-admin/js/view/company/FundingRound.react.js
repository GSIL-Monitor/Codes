var React = require('react');
var $ = require('jquery');


// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormSelect = require('../form/FormSelect.react');

var ActionUtil = require('../../action/ActionUtil');
var FundingAction = require('../../action/FundingAction');
var FundingStore = require('../../store/FundingStore');

var Functions = require('../../util/Functions');



const FundingRound = React.createClass({

    getInitialState() {
        return {};
    },

    render() {
        var detail = this.props.data;
        if (detail == null){
            return null
        }else{

            return(
                <div className="sub-round">
                    <div>
                        <h3>融资详情</h3>

                        <FormSelect label='轮次'
                                    name='round'
                                    value={detail.round}
                                    select = {Functions.roundSelect()}
                                    onChange={this.handleChange} />

                        <FormInput label='轮次描述'
                                   name='roundDesc'
                                   value={detail.roundDesc}
                                   className='input-short'
                                   onChange={this.handleChange} />

                        <FormInput label='金额'
                                   name='investment'
                                   value={detail.investment}
                                   className='input-short'
                                   onChange={this.handleChange} />

                        <FormSelect label='货币'
                                    name='currency'
                                    value={detail.currency}
                                    select = {Functions.currencySelect()}
                                    onChange={this.handleChange} />

                        <FormSelect label='精确性'
                                    name='precise'
                                    value={detail.precise}
                                    select = {Functions.preciseSelect()}
                                    onChange={this.handleChange} />

                        <FormSelect label='类型'
                                    name='fundingType'
                                    value={detail.fundingType}
                                    select = {Functions.fundingTypeSelect()}
                                    onChange={this.handleChange} />

                        <FormInput label='时间'
                                   name='fundingDate'
                                   value={detail.fundingDate}
                                   className='input-short'
                                   onChange={this.handleChange} />

                        <FormInput label='投前估值'
                                   name='preMoney'
                                   value={detail.preMoney}
                                   className='input-short'
                                   onChange={this.handleChange} />

                        <FormInput label='投后估值'
                                   name='postMoney'
                                   value={detail.postMoney}
                                   className='input-short'
                                   onChange={this.handleChange} />

                    </div>

                    <div className="div-operate">
                        <a className="a-red m-t-10 m-l-10 left" onClick={this.handleDelete}>删除</a>
                        <button className="btn btn-navy" onClick={this.handleUpdate}>更新</button>
                    </div>
                </div>
            )
        }

    },

    handleChange(event){
        this.props.onChange(event);
    },

    handleUpdate(){
        var store = FundingStore.get();
        var old_store = FundingStore.getOld();
        var old;
        var update;
        for(var i in store){
            if(store[i].funding.id == this.props.data.id){
                update = store[i].funding;
                old = old_store[i].funding;
            }
        }

        ActionUtil.checkUpdate(old, update);
    },

    handleReset(){
        var store = FundingStore.get();
        var old_store = FundingStore.getOld();
        var old;
        var update;
        for(var i in store){
            if(store[i].funding.id == this.props.data.id){
                update = store[i].funding;
                old = old_store[i].funding;
            }
        }

        ActionUtil.reset(old, update);
    },

    handleDelete(){
        var store = FundingStore.getRound();
        var round = store.funding.round;
        var roundName = Functions.getRoundName(round);
        var info = roundName+'轮融资记录';
        ActionUtil.delete(info);
    }


});


module.exports = FundingRound;
