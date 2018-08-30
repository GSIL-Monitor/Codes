var React = require('react');
var Reflux = require('reflux');

var DemoDayUtil = require('../../../../../webapp-site/js/util/DemoDayUtil');
var CompanyUtil = require('../../../../../webapp-site/js/util/CompanyUtil');
var StarRating = require('../score/StarRating.react');

var Functions = require('../../../../../react-kit/util/Functions');
var FindNone = require('../../../../../react-kit/basic/DivFindNone.react');


const PreScores = React.createClass({

    render(){
        var list = this.props.list;
        if(list == null) return <FindNone />
        if(list.length ==0) return <FindNone />;

        var id = this.props.id;
        return(
            <div className="dd-score-list">
                <div className="preScore-item dd-list-head">
                    <div className="m-prescore-name">项目名</div>
                    <div>推荐机构</div>
                    <div>地址</div>
                    <div>融资</div>
                    <div>初筛</div>
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
        var data = this.props.data;
        var id = this.props.id;
        var link =  "./#/demoday/"+id+"/company/"+data.code+"/preScore";

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

        var preScore = data.score;
        if(Functions.isNull(preScore)){
            preScore = 'N/A';
        }


        return(
            <div className={className}>
                <div className="m-prescore-name">
                    <a href={link}> {data.name} </a>
                </div>
                <div>{data.orgName}</div>
                <div>{data.location}</div>
                <div>{fundingInfo}</div>
                <div>
                    {preScore}
                </div>
            </div>
        )
    }
});

module.exports = PreScores;
