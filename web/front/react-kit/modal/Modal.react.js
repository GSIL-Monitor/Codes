var React = require('react');
var $ = require('jquery');

var AddFunding = require('../company/modal/content/AddFunding.react');
var AddFundingInvestor = require('../company/modal/content/AddFundingInvestor.react');

var Modal = React.createClass({

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
                        <ModalContent data={this.props.content} />
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
        var content = this.props.data;
        if (content == null){
            return null
        }
        else if(content == "AddFunding"){
            return(
                <AddFunding />
            )
        }
        else if(content == "AddFundingInvestor"){
            return(
                <AddFundingInvestor />
            )
        }

    }
});

module.exports = Modal;
