var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var DivExtend = require('../../../../../react-kit/basic/DivExtend.react');
var FundingList = require('./FundingList.react');


const Fundings = React.createClass({

    render(){
        var data = this.props.data;
        var list = data.fundings;
        if(list == null) return null;
        if(list.length ==0) return null;
        var showAll = data.fundingAll;
        var more;
        var len = 5;
        if(list.length > len){
            list = CompanyUtil.getSubList(list, len, showAll);
            if(showAll){
                more = <DivExtend type="less" extend={this.extend}/>
            }
            else{
                more = <DivExtend type="more" extend={this.extend}/>
            }
        }

        var className = 'section-body ';
        var company = data.company;
        //if(Functions.isNull(company.round) ||
        //    company.round == 0 ||
        //    Functions.isNull(company.investment) ||
        //    company.investment == 0){
        //    className += ' m-t--10';
        //}else{
        //}


        return(
            <section className={className}>
                <div className="section-round">
                    <div className="section-name name4">
                        融资<br/>历程
                    </div>
                </div>
                <div className="section-content funding-section">
                    <FundingList data={list}/>

                    {more}
                </div>
            </section>
        )
    },

    extend(){
        CompanyActions.showFundingAll();
    }

});





module.exports = Fundings;
