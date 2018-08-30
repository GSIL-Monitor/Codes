var React = require('react');

var HeaderActions = require('../../../../react-kit/action/HeaderActions');
var ColdCall = require('../../view/coldCall/ColdCall.react');

var RouterColdCall = React.createClass({

    componentWillMount() {
        HeaderActions.router('coldcall');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('coldcall');
    },

    render(){
        var type = this.props.params.type;
        if(type=='match'){
            type=1;
        }
        else{
            type=0;
        }

        return(
         <ColdCall type={type} />
        )
    }
});

module.exports = RouterColdCall;
