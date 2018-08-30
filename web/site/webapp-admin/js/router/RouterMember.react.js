var React = require('react');
var Footer = require('../view/basic/Footer.react');

var CompanyNav = require('../view/basic/CompanyNav.react.js');
var Member = require('../view/company/Member.react');
var MemberModal = require('../view/company/modal/MemberModal.react');




var RouterMember= React.createClass({

    render(){
        var id = this.props.params.id;
        //console.log(id);
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <CompanyNav id={id} />
                        <Member id={id} />
                    </div>
                </div>
                <MemberModal />
                <Footer />
            </div>
        )
    }
});

module.exports = RouterMember;
