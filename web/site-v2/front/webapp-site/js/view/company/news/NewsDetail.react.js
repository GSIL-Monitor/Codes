var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var NewsStore = require('../../../store/company/NewsStore');
var NewsActions = require('../../../action/company/NewsActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var DivExtend = require('../../../../../react-kit/basic/DivExtend.react');

const NewsDetail = React.createClass({
    mixins: [Reflux.connect(NewsStore, 'data')],

    componentWillMount() {
        NewsActions.initNewsDetail(this.props.companyId, this.props.newsId);
    },

    componentWillReceiveProps(nextProps) {
        if( this.props.companyId == nextProps.companyId &&
            this.props.newsId == nextProps.newsId)
            return;
        NewsActions.initNewsDetail(nextProps.companyId, nextProps.newsId);
    },

    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;

        var data = state.data.news;
        var contents = data.contents;
        if(contents.length == 0)
            return null;

        return (
            <div className="">
                <div className="ibox">
                    <div className="ibox-content">
                        <div className="text-center m-b-10">
                            <h2>
                                <strong>{data.news.title}</strong>
                            </h2>
                            <div className="m-t-5 text-center">
                                <span className="tl-stamp ">
                                    <i className="fa fa-clock-o m-r-5"></i>
                                    {data.news.date}
                                </span>
                            </div>
                        </div>
                        <div className="news-content">
                            {contents.map(function(result,index){
                                return <p key={index}>{result.content}</p>
                            })}
                        </div>
                    </div>
                </div>
            </div>
        )
    }

});


const NewsNav = React.createClass({
    render(){

    }
});


module.exports = NewsDetail;