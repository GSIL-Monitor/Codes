var React = require('react');
var $ = require('jquery');

var Header = React.createClass({

    handleClick: function(){
        $('.sidebar').toggle();
    },

    render: function() {

        return (
            <header className="header" role="banner">
                <div className="header-bar" onClick={this.handleClick}>
                    <i className="fa fa-bars"></i>
                </div>
                <div className="container">
                    <div className="header-logo left m-r-30">
                        <h3>未语筹谋</h3>
                    </div>

                    <div className="search left" role="search">
                        <form acceptCharset="UTF-8" action="/webapp-admin/#/search">
                            <input type="text" className="search-input" placeholder="Search"
                                   tabIndex="1" autoCapitalize="off" onClick={this.searchClick}/>
                        </form>
                    </div>

                    <div className="search-hint" >
                        <div>
                            Teambiton
                        </div>
                        <div>
                            aiche
                        </div>
                        <div>
                            baoyang
                        </div>

                    </div>

                    <nav className="left">
                        <ul className="header-nav" role="navigation">

                            <li>
                                <a href="#/company/list">公司</a>
                            </li>

                            <li>
                                <a>众筹</a>
                            </li>

                            <li>
                                <a href="#/investor/new">投资人</a>
                            </li>

                            <li>
                                <a href="#/member/new">创业者</a>
                            </li>

                        </ul>

                    </nav>

                    <ul className="user-nav right" >

                        <li>
                            <button className="btn btn-navy ">注册</button>
                        </li>

                        <li>
                            <button className="btn btn-white">登录</button>
                        </li>

                    </ul>

                </div>

            </header>


        );
    },

    searchClick(e){
        $('.search-hint').show();
        e.stopPropagation();
    }

});





module.exports = Header;
