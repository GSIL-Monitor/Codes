var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var InitActions = require('../../../../../webapp-site/js/action/InitActions');
var InitStore = require('../../../../../webapp-site/js/store/InitStore');
var Functions = require('../../../../../react-kit/util/Functions');
var Overview = require('../../company/Overview.react');
var ScoreCtrl = require('./ScoreCtrl.react');


const CompanyScore = React.createClass({

    mixins: [Reflux.connect(InitStore, 'data')],

    componentWillMount() {
        InitActions.initDemoDayScore(this.props.id, this.props.code, this.props.type);
    },

    componentWillReceiveProps(nextProps) {
        InitActions.initDemoDayScore(nextProps.id, nextProps.code, nextProps.type);
    },

    render(){
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;
        var code = data.code;
        var type = data.scoreType;
        var id = data.demodayId;

        return(
            <div className="m-body">

                <Overview code={code} from={type} id={id} />
                <ScoreCtrl id={id} code={code} type={type} />

            </div>
        )
    }

});



module.exports = CompanyScore;

