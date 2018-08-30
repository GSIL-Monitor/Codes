var React = require('react');
var Search = require('../view/search/Search.react.js');

var Footer = require('../../../react-kit/basic/Footer.react');


var RouterSearch = React.createClass({

    render(){
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <Search />
                    </div>
                </div>
                <Footer />
            </div>
        )
    }
});

module.exports = RouterSearch;
