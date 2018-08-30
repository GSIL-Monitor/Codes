var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompsStore = require('../../../store/company/CompsStore');
var CompsActions = require('../../../action/company/CompsActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var Comps = require('./Comps.react');
var UpdateComps = require('./UpdateComps.react');

const CompsCtrl = React.createClass({
    mixins: [Reflux.connect(CompsStore, 'data')],

    componentWillMount() {
        CompsActions.get(this.props.id);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.id == nextProps.id) return;
        CompsActions.get(nextProps.id);
    },

    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;

        var data= state.data;
        if(data.update)
            return <UpdateComps data={data}/>
        else
            return <Comps data={data} />
    }

});


module.exports = CompsCtrl;