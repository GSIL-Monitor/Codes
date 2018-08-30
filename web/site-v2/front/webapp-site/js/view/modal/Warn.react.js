var React = require('react');
var $ = require('jquery');

var Warn = React.createClass({

    render(){

        return (
            <div className="modal" id={this.props.id}>
                <div className="modal-mask" onClick={this.handleCancel}></div>
                <div className="warn-body" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                    <div className="warn-header">
                        <span className="warn-name">{this.props.name}</span>

                        <div className="close right" onClick={this.handleCancel}>
                            <span>×</span>
                        </div>
                    </div>

                    <div className="warn-content">
                        {this.props.content}
                    </div>

                    <div className="warn-comfirm">
                        <button className="btn btn-red " onClick={this.handleComfirm}>确认</button>
                        <button className="btn btn-white" onClick={this.handleCancel}>取消</button>
                    </div>

                </div>
            </div>

        )
    },


    handleCancel(){
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


module.exports = Warn;