var React = require('react');
var $ = require('jquery');

var Functions = require('../../util/Functions');

var LastInvestor = React.createClass({
    render: function(){
        var data = this.props.data;
        if (data.id == -1){
            return(
                <div className="right-part">
                    <div>
                        <div className="source-list">
                            <div className="source-info">
                                <div className="source-head">
                                    <label>无新增加记录</label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }else{
            var types = Functions.investorTypeSelect();
            //console.log(types)
            var typeName = "";
            for(var i in types){
                if( types[i].value == data.type ){
                    typeName = types[i].name;
                    break
                }
            }
            return(
                <div className="right-part">
                    <div>
                        <div className="source-list">
                            <div className="source-info">
                                <div className="source-head">
                                    <label>新增加记录</label>
                                </div>
                                <div className="source-detail">
                                    <div>ID: {data.id}</div>
                                    <div>类型: {typeName}</div>
                                    <div>姓名: {data.name}</div>
                                    <div>网站: {data.website}</div>
                                    <div>域名: {data.domain}</div>
                                    <div>简介: {data.description}</div>
                                    <div>投资阶段: {data.stage}</div>
                                    <div>投资领域: {data.field}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }
    },
});

module.exports = LastInvestor;