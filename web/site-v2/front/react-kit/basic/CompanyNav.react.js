var React = require('react');
var ReactRouter = require('react-router');
var Link = ReactRouter.Link;

const CompanyNav = React.createClass({
    render(){
        var id = this.props.id;
        var link_company = '#/company/basic/'+id;
        var link_funding = '#/company/funding/'+id;
        var link_member = '#/company/member/' + id;
        return(
            <nav className="nav-c">
                <ul>
                    <li>
                        <a href={link_company}>Company</a>
                    </li>
                    <li>
                        <a>Product</a>
                    </li>
                    <li>
                        <a href={link_funding}>Funding</a>
                    </li>
                    <li>
                        <a href={link_member}>Member</a>
                    </li>
                    <li>
                        <a>News</a>
                    </li>
                    <li>
                        <a>Crowdfunding</a>
                    </li>
                </ul>
            </nav>
        )
    }
});


module.exports = CompanyNav;
