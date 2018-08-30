var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var UserStore = require('../store/UserStore');
var UserActions = require('../action/UserActions');

var Functions = require('../../../react-kit/util/Functions');
var UserUtil = require('../util/UserUtil');


var Login = React.createClass({

    mixins: [Reflux.connect(UserStore, 'data')],

    componentWillMount(){
        var url = UserUtil.getParameterByName("returnurl");
        UserActions.setReturnurl(url);
    },

    render(){
        var username;
        var password;
        var login = "登录";
        var errorClass = "login-error ";
        var error;
        var userFocus;
        var pwdFocus;

        var autoLogin = true;

        //console.log(this.state);

        if(!Functions.isEmptyObject(this.state)){
            var data = this.state.data;
            //console.log(data);

            if( data.verified ){
                var url = "/";
                if( data.setting == true){
                    url = "/#/setting";
                }
                else {
                    if( data.grade == 33010) {
                        if (data.returnurl == null || data.returnurl == "") {
                            url = "/";
                        }
                        else {
                            url = data.returnurl;
                        }
                    }
                    else{
                        url = "/#/demoday";
                    }
                }
                if(Functions.browserVersion() == "mobile"){
                    url = "/mobile" + url;
                }
                window.location.href = url;
                return(<div/>);
            }

            username = data.username;
            password = data.password;

            autoLogin = data.autoLogin;

            if(data.login){
                login = "登录中...";
            }

            if(!Functions.isNull(data.error)){
                errorClass += "show";
                error = data.error;


                if(data.error.indexOf("用户") > 0){
                    userFocus = true
                }else{
                    pwdFocus = true;
                }

            }else{
                errorClass += "hide";
            }

        }


        return(
            <div className="m-t-40">

                <div className="m-b-20 text-center">
                    <h2>烯牛数据</h2>
                </div>

                <div className="form-login">

                    <h3 className="m-b-10">欢迎回来</h3>

                    <div className={errorClass}>{error}</div>

                    <div className="form-group">
                        <input type="text"
                               className="form-control"
                               placeholder="用户名/邮件"
                               name="username"
                               ref="username"
                               value={username}
                               id="username"
                               onChange={this.handleChange}
                               onKeyDown={this.keyDown} />
                    </div>
                    <div className="form-group">
                        <input type="password"
                               id="password"
                               className="form-control"
                               placeholder="密码"
                               name="password"
                               value={password}
                               id="password"
                               onChange={this.handleChange}
                               onKeyDown={this.keyDown} />
                    </div>
                    <div className="form-group">
                        <input type="checkbox" onChange={this.handleCheck} checked={autoLogin} name="autoLogin" /> <i></i> 自动登录
                    </div>

                    <button type="submit"
                            className="btn btn-blue full-width"
                            onClick={this.hanleClick}>
                        {login}
                    </button>

                    <div className="m-t-10">
                        <a className="a-forget left" href="#/forgetpwd">忘记密码?</a>
                        <a className="a-register right hide" href="register.html">注册</a>
                    </div>

                </div>

            </div>
        )
    },

    keyDown(e){
        if(e.keyCode === 13){
            this.hanleClick();
        }
    },

    handleChange(event){
        UserActions.change(event.target.name, event.target.value);
    },

    handleCheck(event){
        UserActions.autoLogin(event.target.checked);
    },

    hanleClick(){
        if(!this.state.login){
            UserActions.login($("#username")[0].value, $("#password")[0].value);
        }
    }
});


module.exports = Login;
