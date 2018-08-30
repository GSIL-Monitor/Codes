var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../../action/demoday/DemoDayActions');
var DemoDayStore = require('../../../store/demoday/DemoDayStore');
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

        var updateBtn;
        if(data.commitOrg){
            if(update)
                updateBtn = <span>
                                <a className="comfirm-company update-company" onClick={this.comfirm}>
                                    确定
                                </a>

                                <a className="update-company" onClick={this.update}>
                                    取消
                                </a>
                            </span>;
            else
                updateBtn = <a className="update-company" onClick={this.update}>修改</a>;

        }


        var score;
        if(data.type == 'preScore' || data.type == 'prescore'){
            score =  <PreScore data={data}/>
        }
        if(data.type == 'score'){
            score =  <Score data={data}/>
        }

        var browser = Functions.browserVersion();
        if(browser == 'mobile'){
            $('.demoday-score').css({'position': 'relative', 'margin-left': '20px'});
        }

        return(
            <div className="user-operate demoday-score">
                {score}
                <div className="org-recommendation">
                    <div className="recommend-head">
                        <span>推荐理由</span> {updateBtn}
                    </div>

                    <CompanyRecommendation data={data} update={update}/>

                </div>
            </div>
        )
    },

    update(){
        DemoDayActions.update();
    },

    comfirm(){
        DemoDayActions.comfirm();
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

