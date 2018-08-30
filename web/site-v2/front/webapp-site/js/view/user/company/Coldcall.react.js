var React = require('react');
var ReactDom = require('react-dom');
var Reflux = require('reflux');
var $ = require('jquery');

var UserCompanyStore = require('../../../store/UserCompanyStore');
var UserCompanyActions = require('../../../action/UserCompanyActions');
var Functions = require('../../../../../react-kit/util/Functions');

var ColdcallDetail = require('../../coldcall/ColdcallDetail.react');

const Coldcall = React.createClass({

    render(){
        var data = this.props.data;
        if(data.coldcall == null)
            return null;

        return (
            <div>
                <div className="user-mark user-coldcall m-t-5" onClick={this.ccClick}>
                    <span>任务</span>
                </div>

                <div className="user-cc-content" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                    <div className="user-cc-header">
                        <a className="a-button right" onClick={this.ccClose}>关闭</a>
                    </div>
                    <ColdcallDetail data={data}/>
                </div>
            </div>
        )
    },

    onMouseOver(){
        document.body.style.overflow = 'hidden';
    },

    onMouseOut(){
        document.body.style.overflow = 'auto';
    },

    ccClick(){
        $('.user-cc-content').show();
        $('.container').css('margin-left', '50px');
        $('.header').css('z-index', '-1');
    },

    ccClose(){
        $('.user-cc-content').hide();
        $('.container').css('margin-left', 'auto');
        $('.header').css('z-index', '999');
    }

});



module.exports = Coldcall;