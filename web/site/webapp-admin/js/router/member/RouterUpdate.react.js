var React = require('react');
var Footer = require('../../view/basic/Footer.react');

var UpdateMemberModal = require('../../view/member/modal/UpdateMemberModal.react');
var UpdateForm = require('../../view/member/UpdateForm.react')



var RouterMemberUpdate= React.createClass({

    render(){
        var id = this.props.params.id;
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <UpdateForm id={id}/>
                    </div>
                </div>
                <UpdateMemberModal />
                <Footer />
            </div>
        )
    }
});

module.exports = RouterMemberUpdate;
