var React = require('react');
var ReactRouter = require('react-router');

const ButtonLoadMore = React.createClass({

    render(){
        return(
            <div className="div-add">
                <a className="a-button" onClick={this.add}>
                    <i className="fa fa-plus m-r-5"></i>添加
                </a>
            </div>
        )
    },

    add(e){
        this.props.onClick(e);
    }
});


module.exports = ButtonLoadMore;
