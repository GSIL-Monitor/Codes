var React = require('react');
var Reflux = require('reflux');

var DemoDayUtil = require('../../../util/DemoDayUtil');
var CompanyUtil = require('../../../util/CompanyUtil');
var StarRating = require('../score/StarRating.react');

var Functions = require('../../../../../react-kit/util/Functions');
var FindNone = require('../../../../../react-kit/basic/DivFindNone.react');


const NOPasses = React.createClass({

    render(){
        var list = this.props.list;
        if(list == null) return null;
        if(list.length ==0) return null;

        return(
            <div className="dd-score-list">
                {list.map(function(result, index){
                    return <NOPassItem key={index}
                                       index={index}
                                       data={result}
                            />
                })}
            </div>
        )
    }

});

const NOPassItem = React.createClass({
    render(){
        var index = this.props.index + 1;
        var data = this.props.data;
        var link = "./#/company/"+data.code+"/overview";

        var fundingInfo;
        var investment = data.investment;
        if(investment == null)
            fundingInfo= '未知';
        else
            fundingInfo= CompanyUtil.parseFunding(data);

        var className= 'noPass-item item-unSelect';

        return(
            <div className={className}>
                <div className="noPass-item-rank">{index}</div>
                <div className="dd-item-name">
                    <a href={link}> {data.name} </a>
                </div>
                <div>{data.orgName}</div>
                <div>{data.location}</div>
                <div>{fundingInfo}</div>
            </div>
        )
    }
});

module.exports = NOPasses;
