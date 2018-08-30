var React = require('react');
var $ = require('jquery');

var BasicModal = React.createClass({

    render(){

        return(
            <div className="modal" id={this.props.id}>
                <div className="modal-mask" onClick={this.handleCancel}></div>
                <div className="modal-body" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                    <div className="modal-header">
                        <span className="modal-name" onClick={this.props.confirm}><a>{this.props.name}</a></span>
                        <div className="close right" onClick={this.handleCancel}>
                            <span>×</span>
                        </div>
                    </div>

                    <div className="modal-content">
                        {this.props.content}
                    </div>


                </div>
            </div>

        )
    },

    handleCancel: function(){
        $('.modal').hide();
    },


    onMouseOver(){
        document.body.style.overflow = 'hidden';
    },

    onMouseOut(){
        document.body.style.overflow = 'auto';
    }


});



module.exports = BasicModal;
