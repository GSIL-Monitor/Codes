var React = require('react');
var CompanyList = require('../../view/home/CompanyList.react');
var Footer = require('../../view/basic/Footer.react');


var RouterCompanyList = React.createClass({

    render(){
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <CompanyList />
                    </div>
                </div>
                <Footer />
            </div>
        )
    }
});

module.exports = RouterCompanyList;
