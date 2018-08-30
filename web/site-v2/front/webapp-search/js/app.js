var ReactDOM = require('react-dom');
var Reflux = require('reflux');
var React = require('react');
var RouterConf = require('./router/RouterConf.react');
var View = require('../../react-kit/util/View');
var UserStore = require('../../react-kit/store/UserStore');
var UserActions = require('../../react-kit/action/UserActions');

var HeaderSearch = require('../../react-kit/basic/header/HeaderSearch.react');
var Footer = require('../../react-kit/basic/footer/Footer.react.js');
var Mask = require('../../react-kit/modal/Mask.react');
var Functions = require('../../react-kit/util/Functions');
var ScrollTop = require('../../react-kit/basic/ScrollTop.react');


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
                <HeaderSearch data={this.props.data}/>
                <div className="container">
                    <div className="page-wrapper">
                        <RouterConf />
                        <ScrollTop />
                    </div>
                    <Footer />
                </div>
                <Mask/>
            </div>
        )
    }
});


ReactDOM.render(
    <APP />,
    document.getElementById('app')
);












