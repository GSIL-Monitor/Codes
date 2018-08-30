var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ForgetpwdStore = require('../store/ForgetpwdStore');
var ForgetpwdActions = require('../action/ForgetpwdActions');

var Functions = require('../../../react-kit/util/Functions');


var Resetpwd = React.createClass({

    mixins: [Reflux.connect(ForgetpwdStore, 'data')],

    componentWillMount(){
    },

    render(){
        var password = "";
        var sent = false;
        var errorClass = "login-error ";
        var error;
        var buttonLabel = "重置";

        if(!Functions.isEmptyObject(this.state)){
            var data = this.state.data;

            password = data.password;
            if(data.sending){
                buttonLabel = "重置中...";
            }

            if(data.error != null){
                errorClass += "show";
                error = data.error;
            }else{
                errorClass += "hide";
            }

            sent = data.sent;
        }

        if(sent == false) {
            return (
                <div className="m-t-40">
                    <div className="form-login">

                        <h3 className="m-b-10">重置密码</h3>

                        <div className={errorClass}>{error}</div>

                        <div className="form-group">
                            <input type="password"
                                   className="form-control"
                                   placeholder=""
                                   name="password"
                                   ref="password"
                                   value={password}
                                   onChange={this.handleChange}/>
                        </div>

                        <button type="submit"
                                className="btn btn-blue full-width"
                                onClick={this.hanleClick}>
                            {buttonLabel}
                        </button>
                    </div>

                </div>
            )
        }
        else{
            return (
                <div className="m-t-40">
                    <div className="form-login">
                        <h3 className="m-b-10">重置密码</h3>
                        <div>密码重置成功!</div>
                        <button type="submit"
                                className="btn btn-navy full-width"
                                onClick={this.clickLogin}>
                            登录
                        </button>
                    </div>

                </div>
            )
        }
    },

    handleChange(event){
        ForgetpwdActions.change(event.target.name, event.target.value);
    },

    hanleClick(){
        if(this.state.data==null || !this.state.data.sending){
            ForgetpwdActions.reset(parseInt(this.props.userId), this.props.oneTimePwd);
        }
    },
    clickLogin() {
        window.location.href = "/user/#/login";
    }
});


module.exports = Resetpwd;
