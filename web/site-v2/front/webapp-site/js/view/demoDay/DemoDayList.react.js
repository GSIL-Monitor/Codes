var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayListActions = require('../../action/demoday/DemoDayListActions');
var DemoDayListStore = require('../../store/demoday/DemoDayListStore');
var DemoDayUtil = require('../../util/DemoDayUtil');
var Functions = require('../../../../react-kit/util/Functions');
var FindNone = require('../../../../react-kit/basic/DivFindNone.react');

const DemoDayList = React.createClass({

    mixins: [Reflux.connect(DemoDayListStore, 'data')],

    componentWillMount() {
        DemoDayListActions.getList()
    },

    componentWillReceiveProps(nextProps) {
        DemoDayListActions.getList()
    },

    render(){
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;
        console.log(data);

        if(data.list.length == 0){
            return <FindNone />
        }

        var from = this.props.from;

        return(
            <div className="main-body">
                <ol className="vertical-timeline dd-list">
                    {data.list.map(function(result, index){
                        return <DemoDayItem key={index}
                                            data={result}
                                            selected={data.selectedDemoDay}
                                            from={from} />
                    })}
                </ol>
            </div>
        )
    }

});



const DemoDayItem = React.createClass({

    render(){
        var data = this.props.data;
        var demoday = data.demoday;
        var status = DemoDayUtil.getDemodayStatus(demoday.status);

        var className = 'tl-node dd-item ';
        var detail;
        if(this.props.selected != null && this.props.from != 'admin'){
            if(this.props.selected.demoday.id == demoday.id){
                className += 'dd-selected';
                detail = <DemoDayDetail data={data}/>;
            }
        }

        var holdStartDate = Functions.dateFormat3(demoday.holdStartDate);

        return (
            <li className={className} >
                <div className="dd-item-body">
                    <span className="dd-title" onClick={this.click}
                          onMouseEnter={this.mouseEnter}
                          onMouseLeave={this.mouseLeave}
                          onTouchMove = {this.mouseEnter} >

                        <span className="dd-time">
                            {holdStartDate}
                        </span>
                        <span className="dd-name">
                            {demoday.name}
                        </span>
                        <span className="dd-status">
                            {status}
                        </span>
                    </span>
                </div>
                {detail}
            </li>
        )
    },

    click(){
        var from = this.props.from;
        if(from == 'admin'){
            window.location.href= '/admin/#/demoday/'+this.props.data.demoday.id;
            return;
        }
        window.location.href= './#/demoday/'+this.props.data.demoday.id;
    },

    mouseEnter(){
        DemoDayListActions.hoverDemoDay(this.props.data);
    },

    mouseLeave(){
        //DemoDayListActions.unSelectDemoDay();
    }

});

const DemoDayDetail = React.createClass({
    render(){
        var data = this.props.data;
        var demoday = data.demoday;
        var companies = data.demodayCompanies;
        var link = "./#/demoday/"+demoday.id;
        var status = demoday.status;

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

        var step1Class, step2Class, step3Class, step4Class;
        if(status == 26000){
            step1Class = 'step-selected';
        }else if(status == 26010){
            step2Class = 'step-selected';
        }else if(status == 26024){
            step3Class = 'step-selected';
        }else if(status == 26027){
            step4Class = 'step-selected';
        }

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



        //var submitEndDate = Functions.dateFormat4(demoday.submitEndDate);
        //submitEndDate = submitEndDate + Functions.getWeekday(demoday.submitEndDate);

        return(
            <div className="dd-detail">

                <div className={step1Class}>
                    <a href={link}>
                        项目提交： {submitEndDate} 截止，上传截止前不能打分
                    </a>
                </div>

                <div className={step2Class}>
                    <a href={link}>
                        打分初筛： {preScoreStartDate} ~ {preScoreEndDate}
                    </a>
                </div>


                <div className={step3Class}>
                    <a href={link}>
                        入选公司结果出炉&amp;通知团队：{connectStartDate} 开始
                    </a>
                </div>

                <div className={step4Class}>
                    <a href={link}>
                        Demo day上会公司最终确认： {connectEndDate} 前完成
                    </a>
                </div>


            </div>
        )
    }
});



module.exports = DemoDayList;

