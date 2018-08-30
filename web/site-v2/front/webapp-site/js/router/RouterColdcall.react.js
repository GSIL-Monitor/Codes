var React = require('react');
var Coldcall = require('../view/coldcall/Coldcall.react');
var HeaderActions = require('../../../react-kit/action/HeaderActions');

var RouterColdcall = React.createClass({

    componentWillMount() {
        HeaderActions.router('coldcall');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('coldcall');
    },

    render(){
        var coldcallId = Number(this.props.params.coldcallId);
        return(
            <Coldcall coldcallId={coldcallId}/>
        )
    }
});

module.exports = RouterColdcall;
