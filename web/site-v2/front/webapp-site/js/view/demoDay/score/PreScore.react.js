var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../../action/demoday/DemoDayActions');
var Functions = require('../../../../../react-kit/util/Functions');

var StarRating = require('./StarRating.react');

const PreScore = React.createClass({

    render(){
        var data = this.props.data;
        var disable = true;
        if(data.scoringStatus == 27010)
            disable = false;
        return(
            <StarRating name="初筛选" type="preScore" disable={disable} rated={data.preScore}  rating={data.ratingPreScore}/>
        )
    }


});

module.exports = PreScore;

