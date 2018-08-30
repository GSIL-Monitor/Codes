var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var UserScoreContent = require('../user/company/UserScoreContent.react');
var DemodayScoreContent = require('../demoday/score/modal/ScoreContent.react');
var SearchFilter = require('../../../../webapp-search/js/view/search/modal/MobileFilter.react');

var Modal = React.createClass({

    render(){
        var content;
        var type = this.props.type;
        var comfirmName = this.props.comfirmName;
        var data = this.props.data;

        if(type == 'userScore') {
            content = <UserScoreContent data={data}/>
        }else if(type == 'demodayScore') {
            content = <DemodayScoreContent data={data}/>
        }else if(type == 'searchFilter'){
            content = <SearchFilter data={data}/>
        }

        return (
            <div className="modal" id={this.props.id}>
                <div className="modal-mask"></div>
                <div className="m-modal-body"
                     onMouseOver={this.onMouseOver}
                     onMouseOut={this.onMouseOut}
                     onTouchStart={this.onMouseOver}
                     onTouchEnd = {this.onMouseOut}
                    >
                    <div className="modal-header">
                        <span className="modal-name">{this.props.name}</span>

                        <div className="close right" onClick={this.handleCancel}>
                            <span>×</span>
                        </div>
                    </div>

                    <div className="m-modal-content">
                        {content}
                    </div>

                </div>
            </div>

        )
    },


    handleCancel(){
        if(this.props.cancel != null){
            this.props.cancel();
        }
        $('.modal').hide();
    },

    handleComfirm(){
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