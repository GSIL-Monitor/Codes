var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyUtil = require('../../../../../webapp-site/js/util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');

const FundingList = React.createClass({
    render(){
        var data = this.props.data;
        if(data.length == 0 ) return null;
        return(
            <div>
                {data.map(function (result, index) {
                    return <FundingItem key={index} data={result}/>;
                })}
            </div>
        )
    }

});


const FundingItem = React.createClass({
    render(){
        var data = this.props.data;
        var fundingInfo;
        var funding = data.funding;
        fundingInfo = '融资'+CompanyUtil.parseFunding(funding);

        var firList = data.firList;
        var date = data.funding.fundingDate;
        if(!Functions.isNull(date))
            date = date.substring(0,7);
        else
            date = 'N/A';

        var content = <div className="section-sub-item-content">
                            <div className="funding-money">{fundingInfo}</div>
                            <FIR data={firList}/>
                        </div>

        return(
            <div className="section-sub-item">
                <div className="section-sub-item-name">
                    {date}
                </div>
                {content}
            </div>
        )
    }
});


const FIR = React.createClass({
    render(){
        var data = this.props.data;
        if(data.length == 0)
            return null;

        return(
            <div className="funding-investors">
                <div className="funding-investor-left">投资方：</div>
                <div className="funding-investor-content">
                    {data.map(function (result) {
                        return <Investor key={result.fir.id} data={result}/>;
                    })}
                </div>
            </div>

        )

    }
});

const Investor = React.createClass({
    render(){

        return(
            <div className="investor-info">
                {this.props.data.investor.name}
            </div>
        )

    },

});

module.exports = FundingList;

