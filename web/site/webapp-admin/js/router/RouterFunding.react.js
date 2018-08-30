var React = require('react');
var Footer = require('../view/basic/Footer.react');

var CompanyNav = require('../view/basic/CompanyNav.react');
var Funding = require('../view/company/Funding.react');
var FundingModal = require('../view/company/modal/FundingModal.react');


var RouterFunding= React.createClass({

    render(){
        var id = this.props.params.id;
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <CompanyNav id={id} />
                        <Funding id={id} />
                    </div>
                </div>
                <FundingModal />

                <Footer />
            </div>
        )
    }
});

module.exports = RouterFunding;
