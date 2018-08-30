var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var Functions = require('../../../../../../react-kit/util/Functions');
var DemoDayActions = require('../../../../action/DemoDayActions');
var DemodayStore = require('../../../../store/DemoDayStore');
var ValidateDemodayStore = require('../../../../store/validation/ValidateDemodayStore');


var DemoDayName = require('../../create/DemoDayName.react.js');
var HoldDate = require('../../create/HoldDate.react.js');
var PreScoreDate = require('../../create/PreScoreDate.react.js');
var ScoreDoneDate = require('../../create/ScoreDoneDate.react.js');

const UpdateDemoday = React.createClass({
    mixins: [Reflux.connect(DemodayStore, 'data'),
            Reflux.connect(ValidateDemodayStore, 'validate')],


    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;
        var demoday = this.state.data.newDemoday;
        var oldDemoday = this.state.data.oldDemoday;
        if (Functions.isEmptyObject(demoday)) return null;

        var className ;
        if (this.state.data.change) {
            className = "btn btn-navy cc-org-button";
        }
        else {
            className += " un-change";
        }


        return (
            <div>
                <DemoDayName data={demoday.name} oldData={oldDemoday.name} update={true} onChange={this.change}/>
                <HoldDate data={demoday.holdDate} oldData={oldDemoday.holdDate} onChange={this.change}
                          onBlur={this.blur}/>
                <PreScoreDate data={demoday.preScoreDate} update={true} oldData={oldDemoday.preScoreDate}
                              onChange={this.change}/>
                <ScoreDoneDate data={demoday.scoreDoneDate} update={true} oldData={oldDemoday.scoreDoneDate}
                               onChange={this.change}/>
                <button className={className} onClick={this.handleUpdate}>更新</button>
            </div>
        )
    },

    change(e){
        DemoDayActions.change(e.target.name, e.target.value, true);
    },
    blur(date){
        //update prescoreDate and scoreDoneDate
        DemoDayActions.updateDate(date, true);
    },
    handleUpdate(){
            DemoDayActions.updateDemoday();
    }

});

module.exports = UpdateDemoday;