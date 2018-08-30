var React = require('react');
var $ = require('jquery');

const CompanyHeader = React.createClass({
    render(){
        var company = this.props.data;
        var logo = "http://m.gobivc.com/file/"+company.logo+"/product.png";
        return(
            <div className="company-header">
                <img className="company-logo" src={logo} />
                <div>
                    <div className="company-basic">
                        <p className="company-name">{company.name}</p>
                        <p className="company-brief"> {company.brief} </p>
                        <p> {company.establishDate} @{company.location}</p>

                    </div>

                    <div className="top-operate">
                        <button className="btn btn-blue site-btn m-t-40">关注</button>
                    </div>
                </div>

            </div>
        )
    }

});

module.exports = CompanyHeader;