var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SearchStore = require('../../../store/SearchStore');
var SearchActions = require('../../../action/SearchActions');
var Modal = require('../../../../../mobile-site/js/view/modal/Modal.react');
var Functions = require('../../../../../react-kit/util/Functions');

var MobileFilterModal = React.createClass({

    mixins: [Reflux.connect(SearchStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var data = state.data;

        return  <Modal id="search-filter-modal"
                       name="筛选过滤"
                       type="searchFilter"
                       data = {data}
                       cancel={this.cancel}
            />
    },

    cancel(){
        //SearchActions.cancelFilters();
    }

});

module.exports = MobileFilterModal;