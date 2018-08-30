var React = require('react');
var $ = require('jquery');

const ScrollTop = React.createClass({

    render(){
        return(
            <div className="scroll-top">
                <div className="scroll-top-round" onClick={this.scrollTop}>
                    <i className="fa fa-arrow-up fa-lg"></i>
                </div>
            </div>
        )
    },

    scrollTop(e){
        $(window).scrollTop(0);
    }
});


module.exports = ScrollTop;
