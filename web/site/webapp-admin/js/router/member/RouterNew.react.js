var React = require('react');
var Footer = require('../../view/basic/Footer.react');

var NewMemberModal = require('../../view/member/modal/NewMemberModal.react');
var NewForm = require('../../view/member/NewForm.react')



var RouterMemberNew= React.createClass({

    render(){
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <NewForm />
                    </div>
                </div>
                <NewMemberModal />
                <Footer />
            </div>
        )
    }
});

module.exports = RouterMemberNew;
