var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var UpdateInput = require('./UpdateInput.react');
var UpdateSelect  = require('./UpdateSelect.react');

const UpdateFundingStatus = React.createClass({

    render(){
        if(Functions.isEmptyObject(this.props.data))
            return null;

        var data = this.props.data;

        var updateClass = "section-round ";
        if(data.from == 'demodayAdd'){
            var company = data.updateCompany;
            if( company.round == null||
                company.round == 0 ||
                company.investment == null ||
                company.investment == 0 ||
                company.currency == null ||
                company.currency == 0 ||
                company.preMoney == null ||
                company.preMoney == 0 ||
                company.postMoney == null ||
                company.postMoney == 0 ||
                company.shareRatio ==  null ||
                company.shareRatio == 0  )
                updateClass += 'section-must-update'
        }

        return(
            <section className="section-body">
                <div className={updateClass}>
                    <div className="section-name name4 ">
                        融资<br/>状态
                    </div>
                </div>
                <div className="section-content">

                    <div className="update-hint">输入金额&amp;份额，系统自动得出投前估值&amp;投后估值</div>

                    <UpdateRound data={data} />
                    <UpdateInvestment data={data} />
                    <UpdateEstimation data={data} />

                </div>
            </section>
        )
    }

});


const UpdateRound = React.createClass({
    render(){
        var data = this.props.data;
        var roundClass= 'select-update-round ';
        var round = data.updateCompany.round;
        var old_round = data.company.round;
        if(CompanyUtil.checkCompanyDiff(round, old_round)){
            roundClass += 'update';
        }


        var roundDescClass= 'input-round-desc ';
        var roundDesc = data.updateCompany.roundDesc;
        var old_round_desc = data.company.roundDesc;
        if(CompanyUtil.checkCompanyDiff(roundDesc, old_round_desc)){
            roundDescClass += 'update';
        }

        var roundSelect = Functions.updateRoundSelect();


        return(
            <div className="section-sub-item select-part">
                <div className="section-sub-item-name update-field-name">融资阶段：</div>
                <div className="section-sub-item-content">

                    <UpdateSelect   className={roundClass}
                                    name= 'round'
                                    value= {round}
                                    select={roundSelect}
                                />

                    <UpdateInput className={roundDescClass}
                                 name="roundDesc"
                                 data={roundDesc}
                                 placeholder="轮次描述(A+)"
                        />

                    <span className="m-l-5">(轮次描述不填写)</span>

                </div>
            </div>
        )
    }


});


const UpdateInvestment = React.createClass({
    render(){
        var data = this.props.data;
        var investmentClass= 'input-update-small ';
        var investment = data.updateCompany.investment;
        var old_investment = data.company.investment;
        if(CompanyUtil.checkCompanyDiff(investment*10000, old_investment)){
            investmentClass += 'update';
        }

        var currencyClass= 'select-update-currency ';
        var currency = data.updateCompany.currency;
        var old_currency = data.company.currency;
        if(CompanyUtil.checkCompanyDiff(currency, old_currency)){
            currencyClass += 'update';
        }

        var currencySelect = Functions.currencySelect();

        var shareRatioClass = 'input-update-ratio ';
        var ratio = data.updateCompany.shareRatio;
        var old_ratio = data.company.shareRatio;
        if(CompanyUtil.checkCompanyDiff(ratio, old_ratio)){
            shareRatioClass += 'update';
        }

        //console.log(this.props.data);
        //console.log(investment)

        return(
            <div className="section-sub-item select-part">
                <div className="section-sub-item-name update-field-name">本轮融资：</div>
                <div className="section-sub-item-content">

                    <UpdateInput className={investmentClass}
                                 name="investment"
                                 data={investment}
                                 placeholder="融资金额"
                        />
                    <strong className="m-r-5">万</strong>

                    <UpdateSelect   className={currencyClass}
                                    name= 'currency'
                                    value= {currency}
                                    select={currencySelect}
                        />

                    <UpdateInput className={shareRatioClass}
                                 name="shareRatio"
                                 data={ratio}
                                 placeholder="份额"
                        /> %

                </div>
            </div>
        )
    }

});

const UpdateEstimation = React.createClass({
    render(){
        var data = this.props.data;
        var preMoneyClass= 'input-update-small ';
        var preMoney = data.updateCompany.preMoney;
        var old_preMoney = data.company.preMoney;
        if(CompanyUtil.checkCompanyDiff(preMoney*10000, old_preMoney)){
            preMoneyClass += 'update';
        }

        var postMoneyClass= 'input-update-small ';
        var postMoney = data.updateCompany.postMoney;
        var old_postMoney = data.company.postMoney;
        if(CompanyUtil.checkCompanyDiff(postMoney*10000, old_postMoney)){
            postMoneyClass += 'update';
        }

        return(
            <div className="section-sub-item">
                <div className="section-sub-item-name update-field-name">估值：</div>
                <div className="section-sub-item-content">

                    <UpdateInput className={preMoneyClass}
                                 name="preMoney"
                                 data={preMoney}
                                 placeholder="投前估值"
                        />

                    <UpdateInput className={postMoneyClass}
                                 name="postMoney"
                                 data={postMoney}
                                 placeholder="投后估值"
                        />
                    <span className="text-red">(单位:万)</span>
                </div>
            </div>
        )
    }
});


module.exports = UpdateFundingStatus;
