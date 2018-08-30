var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var UpdateDemoday = require('../demoDay/modal/content/UpdateDemoday.react.js');
var RejectOrgList = require('../demoDay/modal/content/RejectOrgList.react.js');
var UserPreScores = require('../demoDay/modal/content/UserPreScores.react.js');
var UserInfoContent = require('../org/modal/UserInfoContent.react');
var Modal = React.createClass({

    render(){
        var content;
        var type = this.props.type;
        if(type == 'demoday'){
            content =  <UpdateDemoday />;
        }
        if(type == 'rejectOrg'){
            content =  <RejectOrgList />;
        }
        if(type == 'preScores'){
            content =  <UserPreScores />;
        }
        if(type == 'userInfo'){
            content =  <UserInfoContent />;
        }

        return (
            <div className="modal" id={this.props.id}>
                <div className="modal-mask" onClick={this.handleCancel}></div>
                <div className="modal-body" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                    <div className="modal-header">
                        <span className="modal-name">{this.props.name}</span>

                        <div className="close right" onClick={this.handleCancel}>
                            <span>×</span>
                        </div>
                    </div>

                    <div className="modal-content">
                        {content}
                    </div>

                </div>
            </div>

        )
    },


    handleCancel: function(){
        $('.modal').hide();
    },

    handleComfirm: function(){
        this.props.comfirm();
        $('.modal').hide();
    },

    onMouseOver(){
        document.body.style.overflow = 'hidden';
    },

    onMouseOut(){
        document.body.style.overflow = 'auto';
    }

});


module.exports = Modal;