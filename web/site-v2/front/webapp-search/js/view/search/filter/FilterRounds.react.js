var React = require('react');
var $ = require('jquery');

var Functions = require('../../../../../react-kit/util/Functions');
var CommonSearchActions = require('../../../../../react-kit/action/SearchActions');

var SearchActions = require('../../../action/SearchActions');
var SearchStore = require('../../../store/SearchStore');
var SearchUitl = require('../../../util/SearchUtil');

const FilterRound = React.createClass({

    render(){
        var roundSelect = Functions.roundSelect();
        var data = this.props.data;
        var filter = data.filterRounds;
        var from = this.props.from;
        return(
            <div className="span-select-list">
                <h4 className="filter-head">融资轮次</h4>
                {roundSelect.map(function(result, index){
                    return  <RoundItem key={index} data={result} filter={filter} from={from}/>;
                }.bind(this))}
            </div>
        )
    }
});

const RoundItem = React.createClass({

    render(){
        var selectClass = "select-span sector-span ";
        if(SearchUitl.isInList(this.props.data.value, this.props.filter)){
            selectClass += 'filter-selected';
        }

        return  <span className={selectClass} onClick={this.handleClick}>
                     {this.props.data.name}
                </span>
    },

    handleClick(){
        SearchActions.filterRound(this.props.data.value, this.props.from);
    }
});


//var RoundList = React.createClass({
//    render() {
//        return (
//            <div className="div-select-list">
//                { this.props.select.map(function(result){
//                    return  <RoundItem key={result.value}
//                                       name={result.name}
//                                       value={result.value}
//                                       onClick={this.props.onClick}
//                            />;
//                }.bind(this))}
//            </div>
//        );
//    },
//
//    handleChange(event){
//        this.props.onChange(event);
//    }
//});
//
//var RoundItem = React.createClass({
//
//    mixins: [Reflux.connect(SearchStore, 'data')],
//
//    render(){
//
//        //var selectClass = "select-span sector-span ";
//        var selectClass;
//        var state = this.state;
//        if(!Functions.isEmptyObject(state)){
//            if(SearchUitl.isInList(this.props.value, this.state.data.filterRounds)){
//                selectClass = 'filter-selected';
//            }
//        }
//
//
//        return(
//            <div className={selectClass} onClick={this.handleClick} >
//                {this.props.name}
//            </div>
//        )
//    },
//
//    handleClick(){
//        SearchActions.filterRound(this.props.value);
//    }
//});

module.exports = FilterRound;
