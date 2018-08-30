var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var InitActions = require('../../../action/InitActions');
var InitStore = require('../../../store/InitStore');
var Functions = require('../../../../../react-kit/util/Functions');
var DemoDayNav = require('../DemoDayNav.react');
var Overview = require('../../company/Overview.react');

var DemoDayActions = require('../../../action/demoday/DemoDayActions');
var DemoDayStore = require('../../../store/demoday/DemoDayStore');

var Recommendation = require('./Recommendation.react');


const CompleteCompany = React.createClass({

    mixins: [Reflux.connect(InitStore, 'data'),
             Reflux.connect(DemoDayStore, 'demoday')],

    componentWillMount() {
        InitActions.initCompleteCompany(this.props.id, this.props.code);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.id == nextProps.id && this.props.code == nextProps.code) return;
        InitActions.initCompleteCompany(nextProps.id, nextProps.code);
    },

    render(){
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;
        var code = data.code;
        var id = data.demodayId;

        var loadDone;
        var submit;
        if(!Functions.isEmptyObject(this.state.demoday)){
            loadDone = this.state.demoday.loadDone;
            submit = this.state.demoday.submitFlag;
        }

        if(loadDone){
            loadDone = <div className="m-b-20 text-center">
                            <h3>完善信息后点击【提交项目】后再提交</h3>
                        </div>
        }

        if(submit){
            loadDone = null;
            //submit = <div className="m-t-20">
            //                <button className="btn btn-navy full-width" onClick={this.submit}>提交项目</button>
            //            </div>
        }

        //<Recommendation data={data} />

        return(
            <div className="main-body">

                <div className="column three-fourths">
                    <DemoDayNav selected="complete"
                                code= {code}
                                id={id}/>

                    {loadDone}

                    <Overview code={code} from="demodayAdd" id={id}/>

                </div>

                <div className="column one-fourth user-part">
                </div>
            </div>
        )
    },

    submit(){

    }


});

module.exports = CompleteCompany;

