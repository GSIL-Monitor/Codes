var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../react-kit/util/Functions');
var CompanyUtil = require('../util/CompanyUtil');
var RecommendationStore = require('../store/RecommendationStore');
var RecommendationActions = require('../action/RecommendationActions');

var CompanyList = require('../../../react-kit/company/CompanyList.react');

const Recommendation = React.createClass({

    mixins: [Reflux.connect(RecommendationStore, 'data')],

    componentWillMount() {
        RecommendationActions.get();
    },

    componentWillReceiveProps(nextProps) {
        RecommendationActions.get();
    },

    render(){
        if(Functions.isEmptyObject(this.state)) return null;
        var list = this.state.data.list;
        return(
            <RecommendList data={list} />
        )
    }


});

const RecommendList = React.createClass({
    render(){
        var data =this.props.data;
        if(data == null){
            return (
                <div className='recommend-list'>
                    <h3 className="m-t-30 text-center">暂无推荐公司</h3>
                </div>
            )
        }

        return (
                <CompanyList data={data}/>
        )
    }

});




module.exports = Recommendation;

