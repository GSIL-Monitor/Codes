var ReactDOM = require('react-dom');
var Reflux = require('reflux');
var React = require('react');
var RouterConf = require('./router/RouterConf.react');
var View = require('../../react-kit/util/View');
var UserStore = require('../../react-kit/store/UserStore');
var UserActions = require('../../react-kit/action/UserActions');

var MobileSite = require('../../react-kit/basic/header/MobileSite.react');
var MobileFooter = require('../../react-kit/basic/footer/MobileFooter.react');
var Functions = require('../../react-kit/util/Functions');
var Mask = require('../../react-kit/modal/Mask.react');
var ModalList = require('./view/modal/ModalList.react');
var ScrollTop = require('../../react-kit/basic/ScrollTop.react');

var APP= React.createClass({
    mixins: [Reflux.connect(UserStore, 'data')],

    componentWillMount() {
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
       //$('.scroll-top').css({'right':'10px', 'bottom': '20px'});
       return(
           <div>
               <MobileSite data={this.props.data}/>

               <div className="container">
                   <div className="page-wrapper">
                       <RouterConf />
                   </div>
                   <MobileFooter />
               </div>
               <ScrollTop />

               <Mask />
               <ModalList />
           </div>
       )
   }
});



ReactDOM.render(
    <APP />,
    document.getElementById('app')
);











