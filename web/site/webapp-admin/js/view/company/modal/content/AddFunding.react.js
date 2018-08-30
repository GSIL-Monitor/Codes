var React = require('react');
var $ = require('jquery');


// view
var FormInput = require('../../../form/FormInput.react.js');
var FormTextarea = require('../../../form/FormTextarea.react.js');
var FormSelect = require('../../../form/FormSelect.react.js');

var ActionUtil = require('../../../../action/ActionUtil');
var FundingAction = require('../../../../action/FundingAction');
var FundingStore = require('../../../../store/FundingStore');

var Functions = require('../../../../util/Functions');

const AddFunding = React.createClass({

    getInitialState() {
        return FundingStore.getAdd();
    },

    componentDidMount() {
        FundingStore.addChangeListener(this._onChange);
    },

    componentWillUnmount(){
        FundingStore.removeChangeListener(this._onChange);
    },

    render() {
        return(
            <div className="m-l-40">
                <FormSelect label='轮次'
                            name='round'
                            value={this.state.round}
                            select = {Functions.roundSelect()}
                            onChange={this.handleChange} />

                <FormInput label='轮次描述'
                           name='roundDesc'
                           value={this.state.roundDesc}
                           className='input-short'
                           onChange={this.handleChange} />

                <FormInput label='金额'
                           name='investment'
                           value={this.state.investment}
                           className='input-short'
                           onChange={this.handleChange} />

                <FormSelect label='货币'
                            name='currency'
                            value={this.state.currency}
                            select = {Functions.currencySelect()}
                            onChange={this.handleChange} />

                <FormSelect label='精确性'
                            name='precise'
                            value={this.state.precise}
                            select = {Functions.preciseSelect()}
                            onChange={this.handleChange} />

                <FormSelect label='类型'
                            name='fundingType'
                            value={this.state.fundingType}
                            select = {Functions.fundingTypeSelect()}
                            onChange={this.handleChange} />


                <FormInput label='时间'
                           name='fundingDate'
                           value={this.state.fundingDate}
                           className='input-short'
                           onChange={this.handleChange} />

                <FormInput label='投前估值'
                           name='preMoney'
                           value={this.state.preMoney}
                           className='input-short'
                           onChange={this.handleChange} />

                <FormInput label='投后估值'
                           name='postMoney'
                           value={this.state.postMoney}
                           className='input-short'
                           onChange={this.handleChange} />

            </div>
        )
    },

    handleChange(event){
        FundingAction.changeAddFunding(event.target.name, event.target.value);
    },

    _onChange(){
        this.setState(FundingStore.getAdd());
    }

});


module.exports = AddFunding;
