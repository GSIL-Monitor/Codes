var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SearchActions = require('../../action/SearchActions');
var SearchStore = require('../../store/SearchStore');


var Modal = React.createClass({
    mixins: [Reflux.connect(SearchStore, 'data')],

    render(){
        var comfirmName = this.props.comfirmName;
        if (comfirmName==null){
            comfirmName = '确认';
        }

        return(
            <div className="modal" id={this.props.id}>
                <div className="modal-mask"></div>
                <div className="modal-body" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                    <div className="modal-header">
                        <span className="modal-name">{this.props.name}</span>
                        <div className="close right" onClick={this.handleCancel}>
                            <span>×</span>
                        </div>
                    </div>

                    <div className="modal-content">
                        <ModalContent content={this.props.content} />
                    </div>

                    <div className="modal-operate">
                        <button className="btn btn-navy m-r-10" onClick={this.handleComfirm}>
                            {comfirmName}
                        </button>

                        <button className="btn btn-white" onClick={this.handleCancel}>
                            取消
                        </button>
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

var ModalContent = React.createClass({
    render(){
        var content = this.props.content;
        if (content == null){
            return null
        }
        else if(content == "date"){
            return(
                <DateModalContent />
            )
        }
        else if(content == "location"){
            return(
                <LocationModalContent />
            )
        }else if(content == "keyword"){
            return(
                <KeywordModalContent />
            )
        }

    }
});


const DateModalContent = React.createClass({
    render(){
        return(
            <div>
                <input type="text" />
            </div>
        )
    }
});

const LocationModalContent = React.createClass({
    render(){
        return(
            <div>
                <input type="text"></input>
            </div>
        )
    }
});




module.exports = Modal;
