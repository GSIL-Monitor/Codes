var React = require('react');

const ButtonLoadMore = React.createClass({

    render(){
        return(
            <button className="btn btn-white btn-load-more" onClick={this.clickMore}>
                更多
            </button>
        )
    },

    clickMore(e){
        this.props.onClick(e);
    }
});


module.exports = ButtonLoadMore;
