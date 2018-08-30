var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../../../../webapp-site/js/action/demoday/DemoDayActions');
var DemoDayStore = require('../../../../../webapp-site/js/store/demoday/DemoDayStore');
var Functions = require('../../../../../react-kit/util/Functions');
var PreScore = require('./PreScore.react');
var Score = require('./Score.react');

const ScoreCtrl = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    componentWillMount() {
        DemoDayActions.initScore(this.props.id, this.props.code, this.props.type);
    },

    componentWillReceiveProps(nextProps) {
        DemoDayActions.initScore(nextProps.id, nextProps.code, nextProps.type);
    },

    render(){
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;
        var update = data.update;

        var score;
        if(data.type == 'preScore' || data.type == 'prescore'){
            score =  <PreScore data={data}/>
        }
        if(data.type == 'score'){
            score =  <div className="m-demoday-score">
                        <button className="btn btn-blue m-btn" onClick={this.clickScore}>项目打分</button>
                        <button className="btn btn-red m-btn" onClick={this.clickDecide}>投资决策</button>
                     </div>
        }

        return(
            <div className="user-operate">
                {score}

            </div>
        )
    },

    clickScore(){
        $('#demoday-score-modal').show();
    },

    clickDecide(){
        var data  = this.state.data;
        window.location.href = './#/demoday/'+data.id+'/company/'+data.code+'/score/decision';
    }
});

const CompanyRecommendation = React.createClass({
    render(){
        var update = this.props.update;
        var data = this.props.data;

        if(data.demodayCompany == null || data.updateDemodayCompany == null)
            return null;

        if(!update){
            return(
                <pre className="pre-recommendation">
                    {data.demodayCompany.recommendation}
                </pre>
            )
        }
        return(
            <textarea className="recommendation-textarea"
                        value={data.updateDemodayCompany.recommendation}
                        onChange={this.change}/>
        )
    },

    change(e){
        DemoDayActions.changeDemoDayCompany(e.target.value);
    }
});


module.exports = ScoreCtrl;

