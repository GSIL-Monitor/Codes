var React = require('react');
var Reflux = require('reflux');

var DemoDayUtil = require('../../../util/DemoDayUtil');
var CompanyUtil = require('../../../util/CompanyUtil');
var StarRating = require('../score/StarRating.react');

var Functions = require('../../../../../react-kit/util/Functions');
var FindNone = require('../../../../../react-kit/basic/DivFindNone.react');


const PreScores = React.createClass({

    render(){
        var list = this.props.list;
        if(list == null) return <FindNone />
        if(list.length ==0) return <FindNone />;

        //list = DemoDayUtil.sortPreScores(list);
        var id = this.props.id;
        return(
            <div className="dd-score-list">
                <div className="preScore-item dd-list-head">
                    <div className="preScore-item-rank">序号</div>
                    <div>项目名</div>
                    <div>推荐机构</div>
                    <div>公司地址</div>
                    <div>融资金额</div>
                    <div>你的打分</div>
                </div>

                {list.map(function(result, index){
                    return <PreScoreItem key={index}
                                         index={index}
                                         data={result}
                                         id={id}/>
                })}


            </div>
        )
    }

});

const PreScoreItem = React.createClass({
    render(){
        var index = this.props.index + 1;
        var data = this.props.data;
        var id = this.props.id;
        var link = "/#/demoday/"+id+"/company/"+data.code+"/preScore";

        var fundingInfo;
        var investment = data.investment;
        if(investment == null)
            fundingInfo= '未知';
        else
            fundingInfo= CompanyUtil.parseFunding(data);

        var className= 'preScore-item ';
        if(data.scoringStatus == 27030 || data.joinStatus == 28020){
            className += 'item-unSelect';
        }


        return(
            <div className={className}>
                <div className="preScore-item-rank">{index}</div>
                <div className="dd-item-name">
                    <a href={link}> {data.name} </a>
                </div>
                <div>{data.orgName}</div>
                <div>{data.location}</div>
                <div>{fundingInfo}</div>
                <div>
                    <StarRating type="preScore" rated={data.score} disable="true"/>
                </div>
            </div>
        )
    }
});

module.exports = PreScores;
