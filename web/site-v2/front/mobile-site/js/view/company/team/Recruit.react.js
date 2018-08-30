var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var RecruitStore = require('../../../../../webapp-site/js/store/company/RecruitStore');
var RecruitActions = require('../../../../../webapp-site/js/action/company/RecruitActions');

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


const Jobs = React.createClass({

    render(){
        var jobs = this.props.data;
        var jobNav;
        if(jobs.length > 5){
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
    }

});



module.exports = TeamDevelop;