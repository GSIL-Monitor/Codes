var React = require('react');
var $ = require('jquery');


// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormSelect = require('../form/FormSelect.react');

var ActionUtil = require('../../action/ActionUtil');
var FundingAction = require('../../action/FundingAction');
var FundingStore = require('../../store/FundingStore');

var SourceFundingInvestor = require('./source/SourceFundingInvestor.react');
var Functions = require('../../util/Functions');


const FundingInvestor = React.createClass({

    getInitialState() {
        return {};
    },

    render() {
        var investors = this.props.data;
        if (investors == null){
            return(
                <div></div>
            )
        }else{
            var id = -1;
            return(
                <div className="sub-investor">
                    <div>
                        <h3>投资方</h3>

                        { investors.map(function(result){
                            id++;
                            return  <Investor id={id} key={result.id}  data={result} />;
                        }.bind(this))}

                        <a className="a-button m-t-10" onClick={this.addClick}> 添加投资方 </a>
                    </div>
                </div>
            )
        }

    },

    addClick(){
        FundingAction.addFundingInvestor();
    }

});

const Investor = React.createClass({
    render(){
        return(
            <div className="text-soft funding-investor" onClick={this.handleClick}>
                <h4>{this.props.data.investor.name}</h4>
                {this.props.data.fundingInvestorRel.investment}
                <InvestorPopover id={this.props.id} data={this.props.data}/>
            </div>
        )
    },

    handleClick(event){
        //this.setState({show: true});
        FundingAction.changeInvestor(this.props.data.fundingInvestorRel.id);
        $('#'+this.props.id).show();
        event.stopPropagation();
    }
});


const InvestorPopover = React.createClass({

    render(){
        var fir = this.props.data.fundingInvestorRel;
        return(
            <div className="pop-right pop-investor hide" id={this.props.id} onClick={this.handleClick}>
                <div className="pop-left-part">
                    <h3>{this.props.data.investor.name}</h3>
                    <FormInput label='投资金额'
                               name='investment'
                               value={fir.investment}
                               className='input-short'
                               onChange={this.handleChange} />

                    <FormSelect label='货币'
                                name='currency'
                                value={fir.currency}
                                select = {Functions.currencySelect()}
                                onChange={this.handleChange} />

                    <FormSelect label='精确性'
                                name='precise'
                                value={fir.precise}
                                select = {Functions.preciseSelect()}
                                onChange={this.handleChange} />

                    <div className="m-t-10 text-right">
                        <a className="a-red m-t-10 m-l-10 left" onClick={this.handleDelete}>删除</a>
                        <button className="btn btn-navy m-r-10" onClick={this.handleUpdate}>更新</button>
                    </div>

                </div>

                <div className="pop-right-part">
                    <SourceFundingInvestor id={fir.id} />
                </div>
            </div>
        )
    },

    handleChange(event){
        FundingAction.changeFIR(event.target.name, event.target.value);
    },

    handleUpdate(){
        $('.pop-investor').hide();
        event.stopPropagation();

        var store = FundingStore.getFIR();
        var old = FundingStore.getOldFIR();
        if(JSON.stringify(store) != JSON.stringify(old))
            FundingAction.updateFIRDB(store);
    },

    handleDelete(event){
        $('.pop-investor').hide();
        event.stopPropagation();

        var store = FundingStore.getFIR();
        console.log(store);
        var round = FundingStore.getRound();
        var fiList= round.fundingInvestorList;
        var investorName;
        for(var i in fiList){
            if(fiList[i].fundingInvestorRel.id == store.id){
                investorName = fiList[i].investor.name;
            }
        }

        var info = '关联的<strong>'+investorName+'</strong>';
        FundingAction.deleteModal(info);
    },

    handleClick(event){
    }

});


module.exports = FundingInvestor;
