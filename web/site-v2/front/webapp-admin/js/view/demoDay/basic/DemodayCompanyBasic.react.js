var React = require('react');
var Reflux = require('reflux');

var Functions = require('../../../../../react-kit/util/Functions');

var DemodayUtil = require('../../../util/DemodayUtil');
var FormSelect = require('../form/FormSelect.react');

var DemoDaySubmit = require('../basic/demodayCompany/DemoDaySubmit.react');
var DemoDayPreScoreDone = require('../basic/demodayCompany/DemoDayPreScoreDone.react');
var DemoDayConnect = require('../basic/demodayCompany/DemoDayConnect.react');
var DemoDayScore=require('../basic/demodayCompany/DemoDayScore.react');

const DemoDayCompanyBasic = React.createClass({

    render(){
        var demodayStatus = this.props.demodayStatus;
        var demodayCompanies = this.props.demodayCompanies;
        if (!demodayCompanies) return null;
        if(demodayStatus==26000||demodayStatus==26005){
            return <DemoDaySubmit demodayCompanies={demodayCompanies} demodayId={this.props.demodayId}/>

        }
        if(demodayStatus==26010||demodayStatus==26020){
            return <DemoDayPreScoreDone demodayCompanies={demodayCompanies}
                                        demodayId={this.props.demodayId}
                                        demodayStatus={demodayStatus}/>
        }
        if(demodayStatus==26024||demodayStatus==26027){
            return <DemoDayConnect  demodayCompanies={demodayCompanies}
                                    demodayId={this.props.demodayId}
                                    demodayStatus={demodayStatus}
                                    updateCompany={this.props.updateCompany}
                                    selectedIds={this.props.selectedIds}/>
        }
        if(demodayStatus==26030||demodayStatus==26040){
                return <DemoDayScore demodayCompanies={demodayCompanies}
                                     demodayId={this.props.demodayId}
                                     demodayStatus={demodayStatus}
                                />
        }
    }
});



module.exports = DemoDayCompanyBasic;

