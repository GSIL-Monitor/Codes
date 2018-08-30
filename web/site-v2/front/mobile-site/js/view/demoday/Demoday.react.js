var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../../../webapp-site/js/action/demoday/DemoDayActions');
var DemoDayStore = require('../../../../webapp-site/js/store/demoday/DemoDayStore');
var Functions = require('../../../../react-kit/util/Functions');

var PreScores = require('./list/PreScores.react');
var Scores = require('./list/Scores.react');

const DemoDay = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    componentWillMount() {
        DemoDayActions.getDemoDay(this.props.id);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.id == nextProps.id) return;
        DemoDayActions.getDemoDay(nextProps.id);
    },

    render(){
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;
        var demoday = data.selectedDemoDay.demoday;
        var companies = data.companies;
        var hint = true;

        var searchList = [];
        if(this.state.search != null){
            searchList = this.state.search.list;
        }

        var status = data.status;
        console.log(data);

        var scoreList;
        if(status == 26000 || status == 26010 || status == 26020){
            scoreList = <PreScores list={companies} id={demoday.id}/>
        }else{
            scoreList = <Scores list={companies} id={demoday.id}/>
        }

        return(
            <div className="main-body dd-body">

                <div className="m-t-5 m-b-5 text-center">
                    <h3>{demoday.name}</h3>
                </div>

                <div className="dd-detail-list">
                    {scoreList}
                </div>

            </div>
        )
    }

});


module.exports = DemoDay;

