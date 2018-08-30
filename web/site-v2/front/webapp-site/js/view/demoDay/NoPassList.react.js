var React = require('react');
var DemoDayActions = require('../../action/demoday/DemoDayActions');
var DemoDayStore = require('../../store/demoday/DemoDayStore');
var Functions = require('../../../../react-kit/util/Functions');
var DemoDayUtil = require('../../util/DemoDayUtil');
var NOPasses = require('./list/NOPasses.react');

var View = require('../../../../react-kit/util/View');

const NoPassList = React.createClass({

    componentDidMount(){
        window.addEventListener('scroll', this.scroll);
    },

    componentWillUnmount(){
        window.removeEventListener('scroll', this.scroll);
    },

    render(){
        var data = this.props.data;
        var noPasses = data.noPasses;
        var noPassCount = data.noPassCount;

        if(noPassCount == 0) return null;

        return(
            <div className="no-pass-list">
                <h4>报名此次Demo Day的项目还有{noPassCount}家</h4>
                <NOPasses list={noPasses}/>
            </div>

        )
    },

    scroll(){
        if(View.bottomLoad(100)){
            DemoDayActions.getNOPasses();
        }
    }
});

module.exports = NoPassList;