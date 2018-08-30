var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../../action/demoday/DemoDayActions');
var DemoDayStore = require('../../../store/demoday/DemoDayStore');
var Functions = require('../../../../../react-kit/util/Functions');

var AddSearch = require('./AddSearch.react');

const AddItem = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data')],

    render(){
        var companies = this.props.companies;
        var searchList = this.props.searchList;
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;


        return(
            <div>
                <div className="dd-submit-title">项目提交</div>
                <AddSearch companies={companies} data={data} list={searchList} />

            </div>
        )
    }


});

module.exports = AddItem;

