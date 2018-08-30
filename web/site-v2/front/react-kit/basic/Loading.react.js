var React = require('react');
var SpinnerCircle = require('./SpinnerCircle.react');

const Loading = React.createClass({

    render(){
        return(
            <div className="text-center m-t-10">
                <SpinnerCircle />
            </div>
        )
    }

});


module.exports = Loading;
