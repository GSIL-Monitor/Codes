var React = require('react');

var HeaderActions = require('../../../../react-kit/action/HeaderActions');
var OrgUser = require('../../view/org/OrgUser.react');

var RouterOrg = React.createClass({

    componentWillMount() {
        HeaderActions.router('org');
    },

    componentWillReceiveProps(nextProps) {
        HeaderActions.router('org');
    },

    render(){
        var id = parseInt(this.props.params.id);
        return(
            <OrgUser id={id}/>
        )
    }
});

module.exports = RouterOrg;
