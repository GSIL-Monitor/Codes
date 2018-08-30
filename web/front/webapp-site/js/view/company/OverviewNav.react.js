var React = require('react');
var $ = require('jquery');

const OverviewNav = React.createClass({
    render(){
        return(
            <div className="company-nav">
                <ul>
                    <li>公司信息</li>
                    <li>产品介绍</li>
                    <li>核心成员</li>
                    <li>团队成长</li>
                    <li>用户数据</li>
                    <li>媒体关注</li>
                    <li>竞争对手</li>
                </ul>
            </div>
        )
    }
});


module.exports = OverviewNav;