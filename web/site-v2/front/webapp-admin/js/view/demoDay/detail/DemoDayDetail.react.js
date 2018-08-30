var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemodayUtil = require('../../../util/DemodayUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var FormDemoday = require('../form/demoday/FormDemoday.react');

const DemodayDetail = React.createClass({

    render(){
        var demoday = this.props.demoday;
        var dateList = DemodayUtil.getDateList(demoday);
        return (

            <div className="section">
                <div>
                <span>
                 <a className="text-blue" onClick={this.edit}>
                     <i className="fa fa-pencil-square-o">修改</i>
                 </a>
                </span>
                    <FormDemoday label="名称" data={demoday.name}/>
                    <FormDemoday label="当前状态" className="text-red" data={DemodayUtil.getDemodayStatus(demoday.status)}/>

                    <h3 className="right"><a className="text-blue" href={this.props.link}>管理系统备选公司</a></h3>
                </div>
                <DemoDayFlow dateList={dateList} status={Number(demoday.status)} demodayId={this.props.demodayId}/>
            </div>
        )
    },
    edit(){
        this.props.onUpdate("demoday");
    }

});

const DemoDayFlow = React.createClass({

    render(){
        var dateList = this.props.dateList;
        var me = this;
        return (
            <section className="section-body">
                <div className="inner-horizontal-scroll">
                    <div className="line"></div>
                    <div className="line-wrap ps-container">
                        {
                            dateList.map(function (result, index) {
                                return <DateItem key={index}
                                                 data={result}
                                                 status={me.props.status}
                                                 demodayId={me.props.demodayId}
                                    />;
                            })
                        }
                    </div>
                </div>
            </section>
        )
    }

});


const DateItem = React.createClass({
    render(){
        var item = this.props.data;
        var className = "spot add-m-l";
        var currentStatus;
        var href;
        if (this.props.status == item.status) {
            className += " demoday-current-node";
            currentStatus="text-red";
            if(this.props.status===26020){
                href= "/admin/#/demoday/" + this.props.demodayId+"/preScores";
            }
        }

        return (
            <div className="item add-width">
                <span className="vline"></span>
                <span className={className}></span>
                <span className="info">
                      <p>
                          <a href={href}>
                              <span  className={currentStatus}>{item.nodeName}</span>
                          </a>
                      </p>
                      <p className="time">
                          <span  className={currentStatus}> {item.nodeDate}</span>

                      </p>
                </span>
            </div>
        )
    }
});


module.exports = DemodayDetail;