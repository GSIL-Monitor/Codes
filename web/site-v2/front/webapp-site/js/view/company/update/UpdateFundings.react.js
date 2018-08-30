var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var ButtonAdd = require('../../../../../react-kit/basic/ButtonAdd.react');

var UpdateInput = require('./UpdateInput.react');

const UpdateFundings = React.createClass({

    render(){
        var fundings;
        if (this.props.data.length > 0){
            fundings = this.props.data.map(function (result, index) {
                return <FundingItem key={index} data={result}/>;
            })
        }

        return(
            <section className="section-body">
                <div className="section-round">
                    <div className="section-name name4">
                        融资<br/>历程
                    </div>
                </div>
                <div className="section-content">
                    <div className="update-hint">点击融资事件，进入修改页面</div>
                    {fundings}

                    <ButtonAdd onClick={this.add} />
                </div>
            </section>
        )
    },

    add(){
        $('#add-funding-modal').show();
    }

});


const FundingItem = React.createClass({


    render(){
        var data = this.props.data;
        var investorInfo;
        var funding = data.funding;
        var investment =  Functions.parseNumber(funding.investment);
        var currency = Functions.getCurrencyStyle(funding.currency);
        currency = "fa fa-xl m-r-1 m-l-5 "+currency;
        currency = <i className={currency} ></i>

        if(investment == 0){
            fundingInfo = '融资金额未知';
        }else{
            fundingInfo = <span>
                            <span>融资</span>
                            {currency}
                            {investment}
                        </span>
        }
        var round = Functions.getRoundName(funding.round);
        var firList = data.firList;


        var className = "label label-develop";

        CompanyUtil.checkFundingDiff(data);


        return(
            <div className={className} onClick={this.select}>
                <span className="m-r-10">{funding.fundingDate}</span>
                <span className="m-r-10">{round} ({funding.roundDesc})</span>
                <span className="m-r-10">{fundingInfo}</span>
                <FIR data={firList}/>
                <i className="fa fa-times m-l-10 label-close right" onClick={this.delete}></i>
            </div>
        )
    },

    select(){
        CompanyActions.selectFunding(this.props.data);
    },

    delete(e){
        CompanyActions.deleteFunding(this.props.data.funding.id);
        e.stopPropagation();
    }
});

const FIR = React.createClass({
    render(){
        var data = this.props.data;
        if(data.length == 0)
            return null;

        return(
            <span>
                <span>投资方：</span>
                {data.map(function (result) {
                    return <Investor key={result.fir.id} data={result}/>;
                })}
            </span>

        )

    }
});

const Investor = React.createClass({
    render(){

        return(
            <span className="m-r-5">
                {this.props.data.investor.name}
            </span>

        )

    }
});

module.exports = UpdateFundings;
