var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompsStore = require('../../../../store/company/CompsStore');
var CompsActions = require('../../../../action/company/CompsActions');
var Functions = require('../../../../../../react-kit/util/Functions');
var CompanySearchInput = require('../../../../../../react-kit/basic/search/CompanyInput.react');

var AddCompsList = require('./AddCompsList.react');

const CompsContent = React.createClass({

    mixins: [Reflux.connect(CompsStore, 'data')],

    render(){
        var state= this.state;
        if(Functions.isEmptyObject(state))
            return null;

        return(
            <div>
                <div className="tag-list">
                    <AddCompsList data={state.data.newList} type='modal'/>
                </div>

                <CompanySearchInput  from="comps" />

            </div>
        )
    },

    add(){
        //<div className="modal-comfirm">
        //    <button className="btn btn-navy m-r-40 m-b-10 m-t-20 right" onClick={this.add}>
        //        {this.props.name}
        //    </button>
        //</div>
        //CompsActions.addNew();
    }
});


module.exports = CompsContent;