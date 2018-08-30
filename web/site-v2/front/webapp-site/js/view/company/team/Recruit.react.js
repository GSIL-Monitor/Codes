var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var RecruitStore = require('../../../store/company/RecruitStore');
var RecruitActions = require('../../../action/company/RecruitActions');

var Functions = require('../../../../../react-kit/util/Functions');

const TeamDevelop = React.createClass({

    mixins: [Reflux.connect(RecruitStore, 'data')],

    componentWillMount() {
        RecruitActions.get(this.props.id);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.id == nextProps.id) return;
        RecruitActions.get(nextProps.id);
    },

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var data = state.data.list;
        if(data.length == 0) return null;

        return (
            <div className="section">
                <span className="section-header">
                    团队成长
                </span>

                <Jobs data={data}/>
            </div>
        )
    }

});


const RecruitSummary = React.createClass({
    render(){
        return(
            <section className="section-body">
                <div className="section-left">
                    <div className="section-round">
                        <div className="section-left-name name4">
                            招聘<br/>需求
                        </div>
                    </div>
                </div>
                <div className="section-right">
                    2015年9月-2015年10月，共计发布8条招聘信息，招聘需求一般。
                    2015年9月-2015年10月，集中在运营岗位。
                </div>
            </section>
        )
    }
});


const RecruitFocus = React.createClass({
    render(){
        return(
            <section className="section-body">
                <div className="section-left">
                    <div className="section-round">
                        <div className="section-left-name name4">
                            地区<br/>分布
                        </div>
                    </div>
                </div>
                <div className="section-right">
                    招聘地区集中在北京,暂无拓展其他地区动向。
                </div>
            </section>
        )
    }
});



const Jobs = React.createClass({

    render(){
        var jobs = this.props.data;
        var jobNav;
        if(jobs.length > 7){
            jobNav = <div className="i-more">
                        <i className="fa fa-angle-double-right"></i>
                    </div>
        }

        return(
            <section className="section-body">
                <div className="inner-horizontal-scroll">
                    {jobNav}
                    <div className="line"></div>
                    <div className="line-wrap ps-container">
                        {
                            jobs.map(function(result, index){
                            return  <JobItem key={index} data = {result} />;
                            })
                        }
                    </div>
                </div>
            </section>
        )
    }

});


const JobItem = React.createClass({
    render(){
        var item = this.props.data.job;
        return(
            <div className="item">
                <span className="vline"></span>
                <span className="spot"></span>
                <span className="info">
                      <p>
                          <a onClick={this.click}>{item.position}</a>
                      </p>
                      <p className="time">
                          {item.startDate.substring(0,10)}
                      </p>
                </span>
            </div>
        )
    },

    click(){
        RecruitActions.select(this.props.data);
    }
});



module.exports = TeamDevelop;