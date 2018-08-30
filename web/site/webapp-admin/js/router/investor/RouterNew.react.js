var React = require('react');
var Footer = require('../../view/basic/Footer.react');

var NewInvestorModal = require('../../view/investor/modal/NewInvestorModal.react');
var NewForm = require('../../view/investor/NewForm.react')



var RouterInvestorNew= React.createClass({

    render(){
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <NewForm />
                    </div>
                </div>
                <NewInvestorModal />
                <Footer />
            </div>
        )
    }
});

module.exports = RouterInvestorNew;
