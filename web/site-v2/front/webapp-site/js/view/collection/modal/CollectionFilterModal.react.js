var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../modal/Modal.react');
var Functions = require('../../../../../react-kit/util/Functions');

var CollectionStore = require('../../../store/collection/CollectionStore');
var CollectionActions = require('../../../action/collection/CollectionActions');

var CollectionFilterModal = React.createClass({

    mixins: [Reflux.connect(CollectionStore, 'data')],

    render(){
        var state = this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var data = state.data;
        return(
            <Modal id="collection-filter-modal"
                   name="集合筛选"
                   type="collectionFilter"
                   comfirmName="确认"
                   data={data}
                />
        )
    }

});



module.exports = CollectionFilterModal;