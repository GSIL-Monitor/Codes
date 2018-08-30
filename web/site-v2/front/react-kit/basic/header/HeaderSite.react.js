var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var UserStore = require('../../store/UserStore');
var UserActions = require('../../action/UserActions');

var SearchInput = require('./../search/SearchInput.react.js');
var Logo = require('./Logo.react');
var HeaderNav = require('./HeaderNav.react');
var UserNav = require('./UserNav.react');

var HeaderSite = React.createClass({
    render(){
        var data = this.props.data;
        var from;
        if(data.org != null){
            if(data.org.grade == 33020)
                from = 'lite';
        }

        var icon = true;
        return (
            <header className="header" role="banner" >

                <div className="container">

                    <Logo />

                    <div className="header-search">
                        <SearchInput className="search-input" value="" icon={icon}/>
                    </div>

                    <HeaderNav from={from}/>

                    <UserNav data={data}/>

                </div>

            </header>
        );
    }

});





module.exports = HeaderSite;
