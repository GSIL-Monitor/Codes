var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var NewCompanyForm = require('./company/create/CreateCompany.react');

var Functions = require('../../../react-kit/util/Functions');

const CreateCompany = React.createClass({


    render(){
        var coldcallId = this.props.coldcallId;
        var demodayId = this.props.demodayId;

        return(
            <div className="main-body">
                <NewCompanyForm coldcallId={coldcallId} demodayId={demodayId}/>
            </div>
        )
    }


});







module.exports = CreateCompany;

