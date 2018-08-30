var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CollectionActions = require('../../../action/collection/CollectionActions');
var Functions = require('../../../../../react-kit/util/Functions');
var TagFilters = require('../filter/TagFilters.react');
var LocationFilters = require('../filter/LocationFilters.react');
var RoundFilters = require('../filter/RoundFilters.react');

const CollectionFilter = React.createClass({

    render(){
        var data = this.props.data;

        return(
            <div>
                <TagFilters data={data} from="collection"/>
                <LocationFilters data={data} from="collection"/>
                <RoundFilters data={data} from="collection"/>

                <div className="modal-comfirm">
                    <button className="btn btn-navy m-r-20 m-b-10 right" onClick={this.comfirmFilter}>
                        {this.props.name}
                    </button>
                </div>
            </div>
        )
    },

    comfirmFilter(){
        CollectionActions.comfirmFilter();
    }
});


module.exports = CollectionFilter;