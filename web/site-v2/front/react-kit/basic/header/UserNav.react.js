var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var UserStore = require('../../store/UserStore');
var UserActions = require('../../action/UserActions');

var SearchInput = require('./../search/SearchInput.react.js');

var Functions = require('../../util/Functions');


var UserNav = React.createClass({

    render(){

        var data = this.props.data;
        var user = data.user;
        var admin = data.admin;
        var org = data.org;
        var adminLi;
        if(admin){
            adminLi = <li onClick={this.clickAdmin}>管理后台</li>
        }
        if(this.props.adminPage){
            adminLi=<li onClick={this.clickSite}>返回首页</li>
        }

        var setting;
        if(data.org != null){
            if(data.org.grade == 33010)
                setting = <li onClick={this.clickSetting}>设置</li>;
        }

        //console.log(data)

        return(
            <div className="user-nav user-login right"
                 onMouseOver={this.userMouseOver}
                 onMouseOut={this.userMouseOut}>
                <i className="fa fa-user fa-lg m-r-10"></i>
                {user.username}

                <div className="dropdown-menu user-popover ">
                    <ul className="user-ul">
                        {adminLi}
                        {setting}
                        <li onClick={this.clickLogout}>退出</li>
                    </ul>
                </div>
            </div>
        )
    },
    clickSite(){
        window.location.href="/#/";
    },

    clickAdmin(){
        window.location.href="/admin/#/";
    },

    clickSetting(){
        window.location.href="/#/setting";
    },

    clickLogin(e) {
        window.location.href="/user/#login";
    },

    clickLogout(e) {
        UserActions.logout();
        window.location.href="/user/#/login";
    },

    userMouseOver(){
        $('.user-popover').show();
    },

    userMouseOut(){
        $('.user-popover').hide();
    }

});


module.exports = UserNav;