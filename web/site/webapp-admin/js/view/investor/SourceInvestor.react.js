var React = require('react');
var $ = require('jquery');

var SourceActionUtil = require('../../action/source/SourceActionUtil');
var Functions = require('../../util/Functions');

var SourceInvestor = React.createClass({
    render: function(){
        var investors = this.props.investors;
        //console.log(investors);

        if (investors == null || investors.length == 0){
            return(<div>无源数据</div>)
        }else{
            return(
                <div className="right-part">
                    <div>
                        <div className="source-list">
                        { investors.map(function(investor) {
                            var img = "";
                            if (investor.logo != null && investor.logo != "") {
                                img = <img src={"/file/" + investor.logo} width="100"/>
                            }

                            var source = SourceActionUtil.getSourceInfo(investor.source, investor.sourceId)
                            var types = Functions.investorTypeSelect();
                            //console.log(types)
                            var typeName = "";
                            for(var i in types){
                                if( types[i].value == investor.type ){
                                    typeName = types[i].name;
                                    break
                                }
                            }

                            return (
                                <div className="source-info" key={investor.id}>
                                    <div className="source-detail">
                                        <div>源: {source.sourceName}</div>
                                        <div>源Url: <a href={source.sourceInvestorUrl}
                                                      target="_blank">{source.sourceInvestorUrl}</a></div>
                                        <div>名称: {investor.name}</div>
                                        <div>类型: {typeName}</div>
                                        <div>Logo: {img}</div>
                                        <div>网站: {investor.website}</div>
                                        <div>简介: {investor.description}</div>
                                        <div>投资阶段: {investor.stage}</div>
                                        <div>投资领域: {investor.field}</div>
                                    </div>
                                </div>
                            )
                        })}
                        </div>
                    </div>
                </div>
            )
        }
    },

});

module.exports = SourceInvestor;