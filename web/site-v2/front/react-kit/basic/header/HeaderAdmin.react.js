var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var UserStore = require('../../store/UserStore');
var UserActions = require('../../action/UserActions');

var SearchInput = require('./../search/SearchInput.react.js');
var Logo = require('./Logo.react');
var HeaderNav = require('./HeaderNav.react');
var UserNav = require('./UserNav.react');

var HeaderAdmin = React.createClass({
    render() {
        var data = this.props.data;
        var icon = true;
        return (
            <header className="header" role="banner">

                <div className="container">

                    <div className="header-logo left m-r-30">
                        <h3><a >管理后台</a></h3>
                    </div>

                    <div className="header-search">
                        <SearchInput className="search-input" value="" icon={icon}/>
                    </div>

                    <HeaderNav from="admin"/>

                    <UserNav data={data} adminPage={true}/>

                </div>

            </header>
        );
    }


});





module.exports = HeaderAdmin;
