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

const AddFundingInvestor = React.createClass({

    getInitialState() {
        return FundingStore.getAddFIR();
    },

    componentDidMount() {
        FundingStore.addFIRChangeListener(this._onChange);
    },

    componentWillUnmount(){
        FundingStore.removeFIRChangeListener(this._onChange);
    },

    render() {
        return(
            <div className="m-l-40">

                <FormInput label='投资金额'
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

                <div className="form-part">
                    <label>投资方</label>
                    <input type="text"
                           className="input-short"
                           name="investorId"
                           value={this.state.investorId}
                           placeholder="投资方ID"
                           onChange={this.handleChange}
                           onClick={this.handleClickInvestor} />

                    <Investor investorUpdate={this.investorChange} onClick={this.handleClickInvestor}/>
                </div>



            </div>
        )
    },

    handleChange(event){
        FundingAction.changeAddFIR(event.target.name, event.target.value);
    },

    investorChange(val){
        FundingAction.changeAddFIR('investorId',val);
        //this.setState({investorId: val})
    },

    handleClickInvestor(){
        $('#find-investor').show();
        event.stopPropagation();
    },

    _onChange(){
        this.setState(FundingStore.getAddFIR());
    }



});


/****************** investor ********************/

const Investor = React.createClass({

    getInitialState: function() {
        return {data: Functions.investorUseful()};
    },

    render(){
        return(
            <div id="find-investor" className="pop-inner pop-right" onClick={this.handleClick}>
                <div>
                    <input type="text"
                           id="input-investor-name"
                           placeholder="输入投资方"
                           className="m-r-10"
                           onKeyDown={this.handleKeyDown}/>

                    <input type="text"
                           id="input-investor-id"
                           placeholder="投资方ID"
                           className="m-r-10" />

                    <button className="btn btn-navy " onClick={this.handleComfirm}>确认</button>
                </div>
                <InvestorList data={this.state.data} />
            </div>
        );
    },

    handleClick(){
        this.props.onClick();
    },


    handleKeyDown(event){
        if(event.keyCode === 13){
            var name = $('#input-investor-name').val();
            var url = "http://localhost/web-admin/api/admin/investor/get?name="+name;
            $.ajax({
                url: url,
                cache: false,
                success: function(data) {
                    $('#input-investor-id').val(data)
                }
            });
        }
    },

    handleComfirm(event){
        var locationId = $('#input-investor-id').val();
        if (locationId !=""){
            this.props.investorUpdate(locationId);
            $('#find-investor').hide();
            event.stopPropagation();
        }
    }

});

const InvestorList =  React.createClass({
    render(){
        return(
            <div className="div-useful m-t-10">
                <h4>部分投资机构</h4>
                <ul>
                    { this.props.data.map(function(result){
                        return <InvestorUseful name={result.name} value={result.value} />;
                    })}

                </ul>
            </div>
        )
    }

});

const InvestorUseful = React.createClass({
    render(){
        return(
            <li onClick={this.handleClick}>
                <span>{this.props.name}</span>
                <strong>{this.props.value}</strong>
            </li>
        )
    },
    handleClick(event){
        $('#input-investor-name').val(this.props.name);
        $('#input-investor-id').val(this.props.value);
    }
});



module.exports = AddFundingInvestor;
