var React = require('react');

var Mask = React.createClass({

    render: function(){
        return(
            <div>
                <div className="mask">
                    <div className="modal-mask"></div>
                    <div className="mask-load">
                        <div className="spinner">
                            <div className="bounce1"></div>
                            <div className="bounce2"></div>
                            <div className="bounce3"></div>
                        </div>
                    </div>
                </div>

                <div className="hint">

                </div>
            </div>
        )
    }

});

module.exports = Mask;


