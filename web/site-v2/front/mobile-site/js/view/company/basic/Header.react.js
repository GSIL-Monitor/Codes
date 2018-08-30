var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../react-kit/util/Functions');


const Header = React.createClass({

    render(){

        var data = this.props.data;
        var company = data.company;

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
            <div className="m-company-header">
                <img className="company-logo" src={logo} />
                <div className="m-company-basic">
                    <p className="company-name">{name}</p>
                    <p className="company-brief"> {brief} </p>
                    <p>{establishDate} {location}</p>

                </div>
            </div>
        )
    }

});


module.exports = Header;