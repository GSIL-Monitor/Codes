var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');

const FundingList = React.createClass({
    render(){
        var data = this.props.data;
        if(data.length == 0 ) return null;
        return(
            <div>
                {data.map(function (result, index) {
                    return <FundingItem key={index} data={result} />;
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
            return <div className="funding-investors"></div>;

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
        var detail;

        if (this.state != null){
            if(this.state.selected || this.state.detailSelected){
                detail = <InvestorDetail data={this.props.data}
                                         onMouseEnter={this.detailMouseEnter}
                                         onMouseLeave={this.detailMouseLeave} />
            }
        }

        return(
            <div className="investor-info"  onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}>
                {this.props.data.investor.name}
                {detail}
            </div>
        )

    },

    onMouseEnter(){
        this.setState({selected: true})
    },

    onMouseLeave(){
        this.setState({selected: false})
    },

    detailMouseEnter(){
        this.setState({detailSelected: true})
    },

    detailMouseLeave(){
        this.setState({detailSelected: false})
    }
});

const InvestorDetail = React.createClass({
    render(){
        var data = this.props.data;
        var investor = data.investor;

        var investment =  data.fir.investment;
        if(investment == null){
            investment = '未知';
        }else{
            investment = Functions.parseNumber();
        }

        return(
            <div className="investor-detail" onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}>
                <div className="arrow-up investor-arrow-up"></div>
                <div className="arrow-up2 investor-arrow-up2"></div>

                <div className="investor-content">
                    <h4>{investor.name}</h4>
                    <div>本轮出资额：{investment}</div>
                    <div>{investor.description}</div>

                </div>
            </div>
        )
    },

    onMouseEnter(){
        this.props.onMouseEnter();
    },

    onMouseLeave(){
        this.props.onMouseLeave();
    }
});


module.exports = FundingList;

