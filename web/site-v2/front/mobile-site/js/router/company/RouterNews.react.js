var React = require('react');
var NewsDetail = require('../../../../webapp-site/js/view/company/news/NewsDetail.react');
var HeaderActions = require('../../../../react-kit/action/HeaderActions');

var RouterNews = React.createClass({

    componentWillMount() {
        HeaderActions.router('news');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('news');
    },

    render(){

        return(
            <NewsDetail companyId={this.props.params.companyId}
                        newsId={this.props.params.newsId} />
        )
    }
});

module.exports = RouterNews;
