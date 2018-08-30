var React = require('react');
var $ = require('jquery');


// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormSelect = require('../form/FormSelect.react');

var ActionUtil = require('../../action/ActionUtil');
var FundingAction = require('../../action/FundingAction');
var FundingStore = require('../../store/FundingStore');
var FundingRound = require('./FundingRound.react');
var FundingInvestor = require('./FundingInvestor.react');

var SourceFundingRound = require('./source/SourceFundingRound.react');

var Functions = require('../../util/Functions');


function get(){
    return FundingStore.get();
};

function getRound(){
    return FundingStore.getRound();
};

function getOld(){
    return FundingStore.getOld();
};


const Funding = React.createClass({

    getInitialState() {
        return {};
    },
    componentDidMount() {
        FundingAction.get(this.props.id);
        FundingStore.addChangeListener(this._onChange);
    },
    componentWillUnmount(){
        FundingStore.removeChangeListener(this._onChange);
    },

    render() {
        $('.nav-c > ul > li:eq(2) > a').css('color', '#1c84c6');

        var olds = this.state.old;
        var detail = this.state.detail;

        if (olds == null || detail == null ){

            return(
                <div className="m-t-30 text-center find-none">
                    <h3>无融资记录</h3>
                    <button className="btn btn-navy m-t-10" onClick={this.addClick}>添加记录</button>
                </div>
            )
        }else{

            var id = this.state.detail.funding.id;
            var i = -1;
            return(
                <div>
                    <nav className="nav-list inner-horizontal-scroll">
                        <ul>
                            { olds.map(function(result){
                                i++;
                                return  <NavDetail key={i} data = {result} navClick={this.handleClick}/>;
                            }.bind(this))}

                        </ul>
                    </nav>
                    <div className="m-t-10 ">
                        <a className="a-button right" onClick={this.addClick}>添加记录</a>
                    </div>
                    <div>
                        <div className="left-part">
                            <FundingRound data={detail.funding} onChange={this.handleChange}/>
                            <FundingInvestor data={detail.fundingInvestorList} />
                        </div>
                        <SourceFundingRound id={id} />
                    </div>
                </div>
            )
        }

    },

    handleChange(event){
        //console.log(this.state.detail);
        FundingAction.change(this.state.detail.funding.id, event.target.name, event.target.value);
    },

    handleClick(id){
        var store = get();
        FundingAction.changeRound(id);
    },

    addClick(){
        FundingAction.addFunding();
    },

    _onChange() {
        this.setState({data: get()});
        this.setState({old: getOld()});
        this.setState({detail: getRound()});

        if(getOld().length == 0){
            $('.find-none').show();
        }
    }

});


const NavDetail =  React.createClass({

    render(){
        var data = this.props.data;
        var roundName = Functions.getRoundName(Number(data.funding.round));
        return(
            <li onClick={this.handleClick} className={getRound().funding.id==data.funding.id?'selected':''}>
                <h3>{roundName}</h3>
                <p>{data.funding.roundDesc}: {data.funding.investment} </p>
            </li>
        )
    },

    handleClick(event){
        this.props.navClick(this.props.data.funding.id);
        //this.props.navClick(this.props.data.funding.id);
    }

});





module.exports = Funding;

