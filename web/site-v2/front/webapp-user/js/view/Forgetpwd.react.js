var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ForgetpwdStore = require('../store/ForgetpwdStore');
var ForgetpwdActions = require('../action/ForgetpwdActions');

var Functions = require('../../../react-kit/util/Functions');


var Forgetpwd = React.createClass({

    mixins: [Reflux.connect(ForgetpwdStore, 'data')],

    componentWillMount(){
    },

    render(){
        var email = "";
        var errorClass = "login-error ";
        var error = "";
        var buttonLabel = "下一步";
        var sent = false;
        if(!Functions.isEmptyObject(this.state)){
            var data = this.state.data;

            email = data.email;
            if(data.sending){
                buttonLabel = "处理中...";
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

                        <h3 className="m-b-10">找回密码</h3>

                        <div className={errorClass}>{error}</div>

                        <div className="form-group">
                            <input type="text"
                                   className="form-control"
                                   placeholder="电子邮件地址"
                                   name="email"
                                   ref="email"
                                   value={email}
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

                        <h3 className="m-b-10">找回密码</h3>

                        <div>找回密码的邮件已发送到您的邮箱{email},请查看邮件并按邮件说明重置您的密码.</div>

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
            ForgetpwdActions.next();
        }
    }
});


module.exports = Forgetpwd;
