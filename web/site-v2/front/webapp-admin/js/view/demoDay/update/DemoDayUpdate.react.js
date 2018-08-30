var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemodayUtil = require('../../../util/DemodayUtil');
var Functions = require('../../../../../react-kit/util/Functions');

var FormDemoday = require('../form/demoday/FormDemoday.react');
var FormUpdateDemoday = require('../form/demoday/FormUpdateDemoday.react');
var FormDemodayStatus = require('../form/demoday/FormDemodayStatus.react');


const DemodayUpdate = React.createClass({
    render(){
        var demoday = this.props.demoday;
        //var dateList = DemodayUtil.getDateList(demoday);
        var dateList = this.props.strDates;
        return (

            <div className="section">
                <div>
                <span>
                 <a className="text-blue m-r-10" onClick={this.props.confirm}>
                     确定
                 </a>
                    <a className="text-blue " onClick={this.cancel}>取消</a>
                </span>
                    <FormUpdateDemoday label="名称"
                                       name="name"
                                       value={demoday.name}
                                       onChange={this.props.onChange}
                                       oldName={this.props.oldName}
                        />
                    <FormDemodayStatus label="当前状态"
                                       name="status"
                                       value={demoday.status}
                                       onChange={this.props.onChange}/>

                    <h3 className="right"><a className="text-blue" href={this.props.link}>管理系统备选公司</a></h3>
                </div>

                <DemoDayFlow dateList={dateList}
                             status={Number(demoday.status)}
                             onChange={this.props.onChange}
                    />

            </div>

        )
    },
    cancel(){
        this.props.onUpdate("demoday")
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
                                return <DateItem key={index} data={result}
                                                 status={me.props.status}
                                                 onChange={me.props.onChange}
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
        if (this.props.status == item.status) {
            className += " demoday-current-node"
        }

        return (
            <div className="item add-width">
                <span className="vline"></span>
                <span className={className}></span>
                <span className="info">
                      <p>
                          <a >{item.nodeName}</a>
                      </p>
                    <p>
                        <input type="text"
                               className="demoday-date-input"
                               name={item.name}
                               value={item.nodeDate}
                               onChange={this.onChange}
                            />
                    </p>
                </span>

            </div>
        )
    },
    onChange(e){
        var date=true;
        this.props.onChange(e,date);
    }
});



module.exports = DemodayUpdate;