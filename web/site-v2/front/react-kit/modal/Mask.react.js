var React = require('react');
var SpinnerCircle = require('../basic/SpinnerCircle.react');

var Mask = React.createClass({

    render: function(){
        return(
            <div>
                <div className="mask">
                    <div className="modal-mask"></div>
                    <div className="mask-load">
                        <SpinnerCircle />
                    </div>
                </div>

                <div className="hint">

                </div>
            </div>
        )
    }

});

module.exports = Mask;


