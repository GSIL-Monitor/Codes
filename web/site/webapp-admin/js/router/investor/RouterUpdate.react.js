var React = require('react');
var Footer = require('../../view/basic/Footer.react');

var UpdateModal = require('../../view/investor/modal/UpdateModal.react');
var UpdateForm = require('../../view/investor/UpdateForm.react')



var RouterInvestorUpdate= React.createClass({

    render(){
        var id = this.props.params.id;
        return(
            <div>
                <div className="container">
                    <div className="page-wrapper">
                        <UpdateForm id={id}/>
                    </div>
                </div>
                <UpdateModal />
                <Footer />
            </div>
        )
    }
});

module.exports = RouterInvestorUpdate;
