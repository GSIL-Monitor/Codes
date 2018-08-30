var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var FormSelect = require('../../../../../../react-kit/form/FormSelect.react');
var FormInput = require('../../../../../../react-kit/form/FormInput.react');
var Functions = require('../../../../../../react-kit/util/Functions');
var AddFundingInvestor = require('./investor/AddFundingInvestor.react.js');
var NewFIR = require('./investor/NewFIR.react');

var CompanyActions = require('../../../../action/CompanyActions');
var CompanyStore = require('../../../../store/CompanyStore');

const FundingContent = React.createClass({

    mixins: [Reflux.connect(CompanyStore, 'data')],

    render(){
        var data= this.props.data;
        if(Functions.isEmptyObject(data))
            return null;
        var funding = data.funding;
        var firList = data.firList;

        var newFIR, addFIR;
        if(!Functions.isEmptyObject(this.state)){
            addFIR = this.state.data.addFIR;
            if(this.state.data.newFIRFlag){
                newFIR = <NewFIR funding={funding} data={addFIR}  type={this.props.type}/>
            }
        }
        return(
            <div>
                <div className="modal-info">
                    <div className="div-add-funding">
                        <h3>基本信息</h3>
                        <FormSelect label='轮次'
                                    name='round'
                                    value={funding.round}
                                    select = {Functions.roundSelect()}
                                    onChange={this.handleChange}
                            />
                        <FormInput label='轮次描述'
                                   name='roundDesc'
                                   className='input-short'
                                   placeholder="例: A+轮"
                                   value={funding.roundDesc}
                                   onChange={this.handleChange} />
                        <FormInput label='金额'
                                   name='investment'
                                   className='input-short'
                                   value={funding.investment}
                                   onChange={this.handleChange}
                                   unit={true}
                            />
                        <FormSelect label='货币'
                                    name='currency'
                                    select = {Functions.currencySelect()}
                                    value={funding.currency}
                                    onChange={this.handleChange} />


                        <FormSelect label='精确性'
                                    name='precise'
                                    select = {Functions.preciseSelect()}
                                    value={funding.precise}
                                    onChange={this.handleChange} />

                        <FormSelect label='类型'
                                    name='fundingType'
                                    select = {Functions.fundingTypeSelect()}
                                    value={funding.fundingType}
                                    onChange={this.handleChange} />


                        <FormInput label='时间'
                                   name='fundingDate'
                                   className='input-short'
                                   placeholder="例: 2016-01-01"
                                   value={funding.fundingDate}
                                   onChange={this.handleChange} />

                        <FormInput label='投前估值'
                                   name='preMoney'
                                   className='input-short'
                                   value={funding.preMoney}
                                   onChange={this.handleChange} />

                        <FormInput label='投后估值'
                                   name='postMoney'
                                   className='input-short'
                                   value={funding.postMoney}
                                   onChange={this.handleChange} />
                    </div>

                    <div className="div-fir">
                        <h3>投资方信息</h3>
                        <div>
                            <a className="a-button right btn-add-fir " onClick={this.add}>添加</a>
                        </div>

                        <AddFundingInvestor data={firList} type={this.props.type}/>

                        {newFIR}

                    </div>
                </div>

                <div className="modal-comfirm">
                    <button className="btn btn-navy m-r-20 m-b-10 right" onClick={this.update}>
                        {this.props.name}
                    </button>
                </div>
            </div>
        )
    },

    handleChange(e){
        if(this.props.type == 'addFunding')
            CompanyActions.changeFunding(e.target.name, e.target.value);
        else {
             CompanyActions.changeSelectedFunding(e.target.name, e.target.value);
        }

    },

    add(){
        CompanyActions.addNewFIR(true);
    },
    update(){
        CompanyActions.updateFundingAndInvestor(this.props.type);
    }
});


module.exports = FundingContent;