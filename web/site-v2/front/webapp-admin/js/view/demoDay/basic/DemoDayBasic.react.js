var React = require('react');

var DemoDayDetail = require('../detail/DemoDayDetail.react');
var DemoDayUpdate = require('../update/DemoDayUpdate.react');

const DemoDayBasic = React.createClass({

    render(){
        if (this.props.updateDemoday) {
            return <DemoDayUpdate demoday={this.props.newDemoday} onUpdate={this.props.onUpdate}
                                  onChange={this.props.onChange} confirm={this.props.confirm}
                                  strDates={this.props.strDates} oldName={this.props.oldDemoday.name}
                                  link={this.props.link}
                />
        }
        else {
            return <DemoDayDetail demoday={this.props.oldDemoday} onUpdate={this.props.onUpdate}
                                  demodayId={this.props.demodayId} link={this.props.link}

                />
        }
    }
});

module.exports = DemoDayBasic;

