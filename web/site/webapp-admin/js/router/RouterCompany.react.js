var React = require('react');
var CompanyNav = require('../view/basic/CompanyNav.react.js');
var Company = require('../view/company/Company.react.js');
var SourceCompany = require('../view/company/source/SourceCompany.react');
var CompanyModalUpdate = require('../view/company/modal/CompanyModal.react');

var Footer = require('../view/basic/Footer.react');


var RouterCompany= React.createClass({

    render(){
        var id = this.props.params.id;
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <CompanyNav id={id} />
                        <Company id={id} />
                        <SourceCompany id={id} />
                    </div>
                </div>
                <CompanyModalUpdate />
                <Footer />
            </div>
        )
    }
});

module.exports = RouterCompany;
