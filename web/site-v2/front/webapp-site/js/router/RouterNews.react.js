var React = require('react');
var NewsDetail = require('../view/company/news/NewsDetail.react');

var RouterNews = React.createClass({

    render(){

        return(
            <NewsDetail companyId={this.props.params.companyId}
                        newsId={this.props.params.newsId} />
        )
    }
});

module.exports = RouterNews;
