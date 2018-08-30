var React = require('react');
var Search = require('../../view/home/Search.react');
var Footer = require('../../view/basic/Footer.react');


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
