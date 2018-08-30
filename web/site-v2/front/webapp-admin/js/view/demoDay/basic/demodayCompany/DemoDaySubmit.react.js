var React = require('react');
var Reflux = require('reflux');

var Functions = require('../../../../../../react-kit/util/Functions');
var DemoDayActions = require('../../../../action/DemoDayActions');
var DemodayUtil = require('../../../../util/DemodayUtil');


const DemoDaySubmit = React.createClass({

    render(){
        var demodayCompanies = this.props.demodayCompanies;
        if (!demodayCompanies) return null;
        var me=this;


        return (
            <div className="m-t-15">
                <h3>备选公司</h3>
                <div className="dd-score-list">
                    <div className="preScore-item  dd-list-head">
                        <div className="admin-demoday-org-rank">序号</div>
                        <div>项目名</div>
                        <div>推荐机构</div>
                        <div>移除项目</div>
                    </div>
                    {
                        demodayCompanies.map(function (result, index) {
                            return <CompanyItem key={index}
                                                index={index}
                                                data={result}
                                                demodayId={me.props.demodayId}

                                />
                        })}
            </div>
                </div>
        )
    }
});


const CompanyItem = React.createClass({


    render(){
        var index = this.props.index + 1;
        var data = this.props.data;
        var href = "/#/demoday/"+this.props.demodayId+"/company/"+data.code+"/preScore";

        return (
            <div className="preScore-item">
                <div className="admin-demoday-org-rank">{index}</div>
                <div>
                    <a href={href}>{data.name} </a>
                </div>
                <div> {data.orgName}</div>
                <div>
                    <a className="a-add" onClick={this.remove}>
                        <i className="fa fa-minus-circle"></i>
                    </a>
                </div>
            </div>
        )
    },

    remove(){
        DemoDayActions.removeDemodayCompany(this.props.data.id);
    }


});



module.exports = DemoDaySubmit;

