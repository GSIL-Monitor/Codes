var React = require('react');
var Functions = require('../../../../../react-kit/util/Functions');
var CompanyUtil = require('../../../util/CompanyUtil');

const FundingStatus = React.createClass({
    render(){
        var company = this.props.company;
        var round = company.round;
        if(Functions.isNull(round) ||
            round == 0 ||
            Functions.isNull(company.investment) ||
            company.investment == 0) return null;

        var roundName = Functions.getRoundName(round);
        var roundDesc = company.roundDesc;
        if(roundName == roundDesc || Functions.isNull(roundDesc)){
            roundDesc = '';
        }else{
            roundDesc = '('+ roundDesc + ')';
        }

        var currency = company.currency;
        var investment = company.investment;
        var postMoney = company.postMoney;

        var needMoney = CompanyUtil.parseRoundFunding(currency, investment);
        var postMoney = CompanyUtil.parseRoundFunding(currency, postMoney);

        if(Functions.isNull(investment)){
            investment = 'N/A';
            needMoney = 'N/A';
            postMoney = '';
        }else{
            postMoney = <span className="m-l-20">投后估值：{postMoney}</span>
        }

        return(
            <section className="section-body m-t--10">
                <div className="section-round">
                    <div className="section-name name4">
                        融资<br/>状态
                    </div>
                </div>
                <div className="section-content">
                    <div className="section-sub-item">
                        <div className="section-sub-item-name">融资阶段：</div>
                        <div className="section-sub-item-content">{roundName} {roundDesc}</div>
                    </div>

                    <div className="section-sub-part">
                        <div className="section-sub-item-name">本轮融资：</div>
                        <div className="section-sub-item-content">
                            {needMoney}
                            {postMoney}
                        </div>
                    </div>

                </div>
            </section>
        )
    }
});

module.exports = FundingStatus;