var React = require('react');
var Overview = require('../view/company/Overview.react');
var Footer = require('../view/basic/Footer.react');


var RouterSearch = React.createClass({

    render(){
        var code = this.props.params.code;
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <Overview code={code}/>
                    </div>
                </div>
                <Footer />
            </div>
        )
    }
});

module.exports = RouterSearch;
