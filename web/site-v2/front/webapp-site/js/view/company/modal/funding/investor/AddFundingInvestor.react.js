var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var FormSelect = require('../../../../../../../react-kit/form/FormSelect.react.js');
var FormInput = require('../../../../../../../react-kit/form/FormInput.react.js');
var Functions = require('../../../../../../../react-kit/util/Functions');

var CompanyStore = require('../../../../../store/CompanyStore');
var CompanyActions = require('../../../../../action/CompanyActions');
var FundingInvestor = require('./FundingInvestor.react.js');

const AddFundingInvestor = React.createClass({

    render() {
        var data = this.props.data;
        return <FIRList data={data}  type={this.props.type} />

    }

});


const FIRList = React.createClass({
    render(){
        var data = this.props.data;
        type= this.props.type;
        if(data.length == 0){
            return <p>无记录</p>
        }

        return(
            <div>
                <div className="fir-list">
                    {data.map(function (result) {
                        return <FIRItem key={result.fir.id} data={result} type={type}/>;
                    })}
                </div>

                <FIRDetail />
            </div>
        )
    }
});

const FIRItem = React.createClass({

    mixins: [Reflux.connect(CompanyStore, 'data')],

    render(){
        var className="label fir-item ";
        var state = this.state;

        if(!Functions.isEmptyObject(state)){
            //console.log(state.selectedFIR)
            if(state.selectedFIR != null){
                //console.log(state.data.selectedFIR.fir.id )
                //console.log(this.props.data.fir.id)
                if(state.data.selectedFIR.fir.id == this.props.data.fir.id){
                    className += "selected";
                }
            }
        }

        return(
            <div className={className} onClick={this.click}>
                {this.props.data.investor.name}
                <i className="fa fa-times m-l-10 label-close right" onClick={this.delete}></i>
            </div>
        )
    },

    //click(){
    //    CompanyActions.selectFIR(this.props.data);
    //},

    delete(){
            CompanyActions.deleteFIR(this.props.data.fir,this.props.type);
    }
});


const FIRDetail = React.createClass({

    mixins: [Reflux.connect(CompanyStore, 'data')],

    render(){
        if(Functions.isEmptyObject(this.state)){
            return null;
        }

        var funding = this.state.data.selectedFunding.funding;
        var fir = this.state.data.selectedFIR;
        return(
            <div className="update-fir">
                <FundingInvestor funding={funding} data={fir} />
            </div>
        )
    }
});




module.exports = AddFundingInvestor;
