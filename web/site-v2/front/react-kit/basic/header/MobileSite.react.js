var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var HeaderStore = require('../../store/HeaderStore');
var HeaderActions = require('../../action/HeaderActions');
var UserActions = require('../../action/UserActions');

var Functions = require('../../util/Functions');
var MobileSearch = require('./MobileSearch.react');


var MobileSite = React.createClass({

    mixins: [Reflux.connect(HeaderStore, 'data')],

    componentWillMount(){
        HeaderActions.init();
    },

    render(){
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.props.data;
        var from;
        if(data.org != null){
            if(data.org.grade == 33020)
                from = 'lite';
        }

        var headerData = this.state.data;
        var show = headerData.mobileListShow;

        var className= '';
        if(show)
            className = 'selected';
        else
            className = '';

        Functions.updateTitle( headerData.router);



        return (
            <div>
                <header className="m-header" role="banner">

                    <div className="container">

                        <span className="m-site-logo">
                            烯牛数据
                        </span>

                        <div className="m-search">
                            <MobileSearch data={headerData} />
                        </div>

                        <div className="m-header-user" >
                            <span className={className} id="site-menu" onClick={this.click}>
                                <i className="fa fa-list fa-lg"></i>
                            </span>
                        </div>

                    </div>

                </header>

                <List show={show} from={from}/>
            </div>
        );
    },

    searchClick(){
        HeaderActions.clickMobileSearch();
    },

    clickHome(){
        window.location.href = './#/';
    },

    click(){
        HeaderActions.clickMobileHeader();
    }

});


const List = React.createClass({
    render(){
        var show = this.props.show;
        if(!show) return null;

        console.log(this.props)

        if(this.props.from == 'lite'){
            return(
                <div className="m-header-list">
                    <ul>
                        <li onClick={this.clickDemoday}>
                            Demo Day
                        </li>
                        <li onClick={this.clickLogout}>
                            退出
                        </li>
                    </ul>
                </div>
            )
        }

        return(
            <div className="m-header-list">
                <ul>
                    <li onClick={this.clickHome}>
                        首页
                    </li>
                    <li onClick={this.clickRecommend}>
                        推荐
                    </li>
                    <li onClick={this.clickDemoday}>
                        Demo Day
                    </li>
                    <li onClick={this.clickSetting}>
                        我的设置
                    </li>
                    <li onClick={this.clickLogout}>
                        退出
                    </li>
                </ul>
            </div>
        )
    },

    clickHome(){
        window.location.href = './#/';
        HeaderActions.clickMobileHeader();
    },

    clickRecommend(){
        window.location.href = './#/recommendation';
        HeaderActions.clickMobileHeader();
    },

    clickDemoday(){
        window.location.href = './#/demoday';
        HeaderActions.clickMobileHeader();
    },

    clickSetting(){
        window.location.href = './#/setting';
        HeaderActions.clickMobileHeader();
    },

    clickLogout(){
        HeaderActions.clickMobileHeader();
        UserActions.logout();
        window.location.href="/user/#/login";
    }

});



module.exports = MobileSite;
