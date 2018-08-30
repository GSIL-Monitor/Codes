var React = require('react');
var Functions = require('../../../../../react-kit/util/Functions');
var CollectionForm = require('./CollectionForm.react.js');

const RoundFilters = React.createClass({

    render(){
        var data = this.props.data;
        var selected = data.selectedRounds;

        var list = Functions.roundSelect();

        var from = this.props.from;

        return(
            <CollectionForm label='阶段' list={list} type='round' selected={selected} from={from}/>
        )
    }

});

module.exports = RoundFilters;