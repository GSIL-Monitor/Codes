var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var Functions = require('../../../../../react-kit/util/Functions');

var UpdateHeader = require('../update/UpdateHeader.react');

const CompanyHeader = React.createClass({

    //mixins: [Reflux.connect(CompanyStore, 'data')],

    render(){
        //if(Functions.isEmptyObject(this.state))
        //    return null;

        var data = this.props.data;
        var company = data.company;

        if(data.update){
            return <UpdateHeader data={data} />
        }else{
            return <HeaderInfo data={company}/>
        }

    }


});

const HeaderInfo = React.createClass({
    render(){
        var company = this.props.data;
        var logo;
        if(company.logo != null){
            logo = "/file/"+company.logo+"/product.png";
        }else{
            logo = "/resources/image/company_logo.png";
        }
        var establishDate = company.establishDate;
        if(establishDate != null){
            establishDate = establishDate.substring(0,7)
        }

        var location = company.location;
        if(location != null){
            location = "@"+location;
        }
        var name=company.name;
        var brief = company.brief;


        return(
            <div className="company-header">
                <img className="company-logo" src={logo} />
                <div>
                    <div className="company-basic">
                        <p className="company-name">{name}
                            <a className="update-company" onClick={this.update}>
                                修改
                            </a>
                        </p>
                        <p className="company-brief"> {brief} </p>
                        <p>{establishDate} {location}</p>

                    </div>

                </div>

            </div>
        )
    },

    update(){
        CompanyActions.update();
    },

    comfirm(){
        CompanyActions.comfirm();
    }
});


module.exports = CompanyHeader;