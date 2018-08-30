var React = require('react');
var Functions = require('../util/Functions');
var CompanyUtil = require('../../webapp-site/js/util/CompanyUtil');

const Fundings = React.createClass({
    render(){
        var data = this.props.data;
        if(data.length == 0 ) return null;
        if(data.length > 3){
            data = CompanyUtil.getSubList(data, 3, false);
        }
        return(
            <section>
                <span className="pop-section-name">融资历程</span>
                <div className="m-t-5">
                    {data.map(function (result, index) {
                        return <FundingItem key={index} data={result}/>;
                    })}
                </div>
            </section>
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

        var content = <div className= "pop-right-content funding-list">
            <div className="pop-funding-money">{fundingInfo}</div>
            <FIR data={firList}/>
        </div>

        return(
            <div className="pop-funding-item">
                <div className="pop-funding-date">
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
            <div className="pop-funding-investors">
                <div className="pop-investor-left">投资方：</div>
                <div className="pop-investor-right">
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

    }
});

module.exports = Fundings;