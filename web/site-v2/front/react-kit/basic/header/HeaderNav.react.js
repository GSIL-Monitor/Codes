var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var HeaderStore = require('../../store/HeaderStore');
var Functions = require('../../util/Functions');

const HeaderNav = React.createClass({

    render(){

        if(this.props.from == 'admin'){
            return <AdminNav />
        }else if(this.props.from == 'lite'){
            return <LiteNav />
        }

        return <SiteNav />
    }

});


const SiteNav = React.createClass({

    mixins: [Reflux.connect(HeaderStore, 'data')],

    render(){
        var homeClass, recommendClass, demoDayClass, createCompanyClass;
        if(!Functions.isEmptyObject(this.state)){
            var router = this.state.data.router;
            Functions.updateTitle(router);

            if(router == 'home'){
                homeClass = 'selected';
            }else if(router == 'recommend'){
                recommendClass = 'selected';
            }else if(router == 'demoDay'){
                demoDayClass = 'selected';
            }else if(router == 'createCompany'){
                createCompanyClass = 'selected';
            }
        }
        return(
            <nav className="left">
                <ul className="header-nav" role="navigation">

                    <li>
                        <a className={homeClass} href="/#/">首页</a>
                    </li>

                    <li>
                        <a className={recommendClass} href="/#/recommendation">推荐</a>
                    </li>

                    <li>
                        <a className={demoDayClass} href="/#/demoday">Demo Day</a>
                    </li>

                    <li>
                        <a className={createCompanyClass} href="/#/company/create">新建公司</a>
                    </li>

                </ul>
            </nav>
        )
    }

});


const LiteNav = React.createClass({
    render(){
        return(
            <nav className="left">
                <ul className="header-nav" role="navigation">

                    <li>
                        <a className="" href="/#/demoday">Demo Day</a>
                    </li>

                </ul>
            </nav>
        )
    }
});

const AdminNav = React.createClass({

    mixins: [Reflux.connect(HeaderStore, 'data')],

    render(){
        var homeClass,coldCallClass,latestClass, orgClass, demoDayClass;
        if(!Functions.isEmptyObject(this.state)){
            var router = this.state.data.router;
            Functions.updateTitle(router);

            if(router == 'home'){
                homeClass = 'selected';
            }
            else if(router == 'org'){
                orgClass = 'selected';
            }else if(router == 'demoDay'){
                demoDayClass = 'selected';
            }
            else if(router=='coldcall'){
                coldCallClass='selected'
            }
        }
        return(
            <nav className="left">
                <ul className="header-nav" role="navigation">

                    <li>
                        <a className={coldCallClass} href="/admin/#/coldCall">Cold Call</a>
                    </li>

                    <li>
                        <a className={orgClass} href="/admin/#/org">机构</a>
                    </li>

                    <li>
                        <a className={demoDayClass} href="/admin/#/demoday">Demo Day</a>
                    </li>

                </ul>
            </nav>
        )
    }
});


module.exports = HeaderNav;