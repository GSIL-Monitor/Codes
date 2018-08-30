var React = require('react');
var Reflux = require('reflux');

var DemoDayActions = require('../../action/demoday/DemoDayActions');
var DemoDayStore = require('../../store/demoday/DemoDayStore');
var DemoDayUtil = require('../../util/DemoDayUtil');
var Functions = require('../../../../react-kit/util/Functions');

const DemoDayNav = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    componentWillMount() {
        DemoDayActions.getDemoDayNav(this.props.id, this.props.code);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.id == nextProps.id && this.props.code == nextProps.code) return;
        DemoDayActions.getDemoDayNav(nextProps.id, nextProps.code);
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
        var companyName = this.state.data.companyName;


        var roundClass, scoreClass, companyClass;
        if(selected == 'demoday'){
            roundClass = 'selected-dark';
            document.title = roundName+' - 绿洲合投';
        }else if(selected == 'score'){
            scoreClass = 'selected-dark';
        }else if(selected == 'company' || selected == 'complete'){
            companyClass = 'selected-dark';
        }

        var link = "/#/demoday/"+id;
        var demodayNav = <a href={link} className={roundClass}>{roundName}</a>;

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

            document.title = scoreName+' - '+roundName+' - 绿洲合投';

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
                            <a className={companyClass}>{companyName} (提交项目)</a>
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

        var demoday = data;
        var submitEndDate = demoday.submitEndDate;
        var preScoreStartDate = demoday.preScoreStartDate;
        var preScoreEndDate = demoday.preScoreEndDate;
        var connectStartDate = demoday.connectStartDate;
        var connectEndDate = demoday.connectEndDate;
        var holdStartDate = demoday.holdStartDate;
        var holdEndDate = demoday.holdEndDate;

        submitEndDate = Functions.dateFormat5(submitEndDate) + '('+
            Functions.getWeekday(submitEndDate)  + ')';

        preScoreStartDate = Functions.dateFormat5(preScoreStartDate) + '('+
            Functions.getWeekday(preScoreStartDate)  + ')';

        preScoreEndDate = Functions.dateFormat5(preScoreEndDate) + '('+
            Functions.getWeekday(preScoreEndDate)  + ')';

        connectStartDate =  Functions.dateFormat5(connectStartDate) + '('+
            Functions.getWeekday(connectStartDate)  + ')';

        connectEndDate = Functions.dateFormat5(connectEndDate) + '('+
            Functions.getWeekday(connectEndDate)  + ')';

        holdStartDate = Functions.dateFormat3(holdStartDate);


        var statusName = DemoDayUtil.getDemodayStatus(status);
        var hintDiv;
        var demoDayDiv;
        if(hint){
            var info;

            if(status == 26000)
                info = <span>{submitEndDate} 截止，上传截止前不能打分</span>;
            else if(status == 26005)
                info = <span>项目提交已结束，请在{preScoreStartDate}进行初筛选打分</span>;
            else if(status == 26010)
                info = <span>初筛选{preScoreEndDate} 截止， 目前备选【{companies.length}】家团队</span>;
            else if(status == 26020)
                info = <span>初筛选截止, 【{passCount}】家通过筛选</span>;
            else if(status == 26024)
                info = <span>通知团队中, 已有【{joinCount}】家确认上会</span>;
            else if(status == 26027)
                info = <span>通知团队结束，确认【{joinCount}】家上会</span>;
            else if(status == 26030)
                info = <span>请在团队路演结束后打分</span>;
            else
                info = <span>此次Demo Day已结束</span>

            hintDiv = <div className="dd-hint">{info}</div>;
            demoDayDiv =  <div className="dd-detail-info">
                            <span>Demo Day时间：<strong>{holdStartDate}</strong></span>
                            <span>当前状态：<strong>{statusName}</strong></span>
                        </div>
        }
        //{scoreNav}

        return(
            <div>
                <div className="dd-nav">
                    <a href="/#/demoday">Demo Day</a>
                    <i className="fa fa-angle-right m-l-10 m-r-10"></i>
                    {demodayNav}

                    {companyNav}
                </div>

                {demoDayDiv}
                {hintDiv}


            </div>
        )


   }
});


module.exports = DemoDayNav;
