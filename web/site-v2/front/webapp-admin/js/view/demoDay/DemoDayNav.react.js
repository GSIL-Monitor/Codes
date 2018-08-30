var React = require('react');
var Reflux = require('reflux');

var DemoDayActions = require('../../action/DemoDayActions');
var DemoDayStore = require('../../store/DemoDayStore');
var DemoDayUtil = require('../../util/DemoDayUtil');
var Functions = require('../../../../react-kit/util/Functions');

const DemoDayNav = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    componentWillMount() {
        DemoDayActions.getDemoDayNav(this.props.id, this.props.code);
    },

    componentWillReceiveProps(nextProps) {
        //DemoDayActions.getDemoDay(nextProps.id);
    },


    render(){
        var hint = this.props.hint;

        if(Functions.isEmptyObject(this.state))
            return null;
        if(this.state.data.selectedDemoDay == null)
            return null;

        var data = this.state.data.selectedDemoDay.demoday;

        var selected = this.props.selected;
        var scoreType = this.props.scoreType;


        var id = data.id;
        var status = data.status;
        var roundName = data.name;
        var preScoreDate = data.preScoreDate.substring(0,10);
        var scoreDoneDate = data.scoreDoneDate.substring(0,10);
        var holdDate = data.holdDate.substring(0,10);
        var companyName = this.state.data.companyName;


        var roundClass, scoreClass, companyClass;
        if(selected == 'demoday'){
            roundClass = 'selected-dark';
            document.title = roundName+' - 未语筹谋';
        }else if(selected == 'score'){
            scoreClass = 'selected-dark';
        }else if(selected == 'company' || selected == 'complete'){
            companyClass = 'selected-dark';
        }

        var link = "/#/demoday/"+id;
        var demodayNav = <a href={link} className={roundClass}>{roundName}</a>;
        if(selected == 'demoday'){
            var scoresLink = '/#/demoday/'+id+'/score';
            var preScoresLink = '/#/demoday/'+id+'/prescore';
            demodayNav = <span>
                            <a href={link} className={roundClass}>{roundName}</a>
                            <i className="fa fa-angle-right m-l-10 m-r-10"></i>
                            <a href={preScoresLink} >初筛选列表</a>
                            <span className="m-l-10 m-r-10">|</span>
                            <a href={scoresLink} >打分列表</a>
                        </span>
        }

        var scoreNav;
        var companyNav;
        if(scoreType != null){
            var scoreName, scoreLink;
            if(scoreType == 'score'){
                scoreName = '打分列表';
                scoreLink = '/#/demoday/'+id+'/score';
            }else{
                scoreName = '初筛选列表';
                scoreLink = '/#/demoday/'+id+'/prescore';
            }

            document.title = scoreName+' - '+roundName+' - 未语筹谋';

            scoreNav = <span>
                            <i className="fa fa-angle-right m-l-10 m-r-10"></i>
                            <a href={scoreLink} className={scoreClass}>{scoreName}</a>
                      </span>;


            if(companyName != null){
                companyNav = <span>
                                <i className="fa fa-angle-right m-l-10 m-r-10"></i>
                                <a className={companyClass}>{companyName}</a>
                            </span>
            }
        }

        if(selected == 'complete'){
            companyNav = <span>
                                <i className="fa fa-angle-right m-l-10 m-r-10"></i>
                                <label>提交项目</label>
                                <i className="fa fa-angle-right m-l-10 m-r-10"></i>
                                <a className={companyClass}>{companyName}</a>
                            </span>
        }

        var companies = this.state.data.selectedDemoDay.demodayCompanies;
        var joinCount = 0;
        var connectCount = 0;
        var passCount = 0;
        for(var i in companies){
            if(companies[i].joinStatus == 28030){
                joinCount++;
            }else if(companies[i].joinStatus == 28010){
                connectCount++;
            }
            if(companies[i].scoringStatus == 27010){
                passCount++;
            }
        }

        var statusName = DemoDayUtil.getDemodayStatus(status);
        var hintDiv;
        var demoDayDiv;
        if(hint){
            var info;
            if(status == 26000)
                info = <span>项目提交截止至 {preScoreDate}</span>;
            else if(status == 26010)
                info = <span>请在 {preScoreDate} 之前完成初筛打分, 目前备选【{companies.length}】家团队</span>;
            else if(status == 26020){
                info = <span>初筛完成, 【{passCount}】家通过筛选</span>;
            }
            else if(status == 26030)
                info = <span>请在团队路演结束后打分</span>;
            else
                info = <span>此次Demo Day 已结束</span>

            hintDiv = <div className="dd-hint">{info}</div>;
            demoDayDiv =  <div className="dd-detail-info">
                            <span>开始时间：<strong>{holdDate}</strong></span>
                            <span>当前状态：<strong>{statusName}</strong></span>
                        </div>
        }

        return(
            <div>
                <div className="dd-nav">
                    <a href="/#/demoday">DemoDay</a>
                    <i className="fa fa-angle-right m-l-10 m-r-10"></i>
                    {demodayNav}
                    {scoreNav}
                    {companyNav}
                </div>

                {demoDayDiv}
                {hintDiv}


            </div>
        )
   }
});

module.exports = DemoDayNav;
