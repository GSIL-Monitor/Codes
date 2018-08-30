var React = require('react');
var $ = require('jquery');

var Logo = require('./Logo.react');
var HeaderNav = require('./HeaderNav.react');
var UserNav = require('./UserNav.react');

var HeaderSearch = React.createClass({

    render: function() {
        var data = this.props.data;
        var from;
        if(data.org != null){
            if(data.org.grade == 33020)
                from = 'lite';
        }


        return (
            <header className="header" role="banner">

                <div className="container">
                    <Logo />

                    <HeaderNav from={from}/>

                    <UserNav data={data}/>

                </div>

            </header>


        );
    },

    searchClick(e){
        $('.search-hint').show();
        e.stopPropagation();
    }

});





module.exports = HeaderSearch;
