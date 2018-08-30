var ReactDOM = require('react-dom');
var React = require('react');
var Reflux = require('Reflux');
var RouterConf = require('./router/RouterConf.react');
var View = require('../../react-kit/util/View');
var UserStore = require('../../react-kit/store/UserStore');
var UserActions = require('../../react-kit/action/UserActions');

var HeaderAdmin = require('../../react-kit/basic/header/HeaderAdmin.react');
var Footer = require('../../react-kit/basic/footer/Footer.react.js');
var Mask = require('../../react-kit/modal/Mask.react');
var ModalList=require('./view/modal/ModalList.react');
var Functions = require('../../react-kit/util/Functions');

var APP= React.createClass({

    mixins: [Reflux.connect(UserStore, 'data')],

    componentWillMount: function() {
        UserActions.checkLoginStatus();
    },

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state)){
            return null;
        }

        var data = state.data;
        if(data.init){
            if(!data.login) {
                var back = window.location.href;
                window.location.href = "/user/#/login?returnurl=" + encodeURIComponent(back);
            }
            else{
                return <Body data={data} />
            }
        }
    }

});

const Body = React.createClass({
    render(){
        return(
            <div>
                <HeaderAdmin data={this.props.data}/>
                <div className="container">
                    <div className="page-wrapper">
                        <RouterConf />
                    </div>
                    <Footer />
                </div>

                <Mask/>
                <ModalList />
            </div>
        )
    }
});

ReactDOM.render(
    <APP />,
    document.getElementById('app')
);


Date.prototype.format = function(fmt)
{
    var o = {
        "M+" : this.getMonth()+1,                 //月份
        "d+" : this.getDate(),                    //日
        "h+" : this.getHours(),                   //小时
        "m+" : this.getMinutes(),                 //分
        "s+" : this.getSeconds(),                 //秒
        "q+" : Math.floor((this.getMonth()+3)/3), //季度
        "S"  : this.getMilliseconds()             //毫秒
    };
    if(/(y+)/.test(fmt))
        fmt=fmt.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));
    for(var k in o)
        if(new RegExp("("+ k +")").test(fmt))
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length==1) ? (o[k]) : (("00"+ o[k]).substr((""+ o[k]).length)));
    return fmt;
};










