var React = require('react');

var AddTagModal = require('../company/modal/tag/AddTagModal.react');

var UpdateFundingModal = require('../company/modal/funding/UpdateFundingModal.react');
var AddFundingModal = require('../company/modal/funding/AddFundingModal.react');

var UpdateFootprintModal = require('../company/modal/footprint/UpdateFootprintModal.react');
var AddFootprintModal = require('../company/modal/footprint/AddFootprintModal.react');

var JobModal = require('../company/modal/team/JobModal.react');
var MemberModal = require('../company/modal/team/MemberModal.react');
var AddCompsModal = require('../company/modal/comps/AddCompsModal.react');

var DecisionModal = require('../demoDay/score/modal/DecisionModal.react');

var CollectionFilterModal = require('../collection/modal/CollectionFilterModal.react');

var ModalList= React.createClass({
    render(){
        return(
            <div>
                <AddTagModal />
                <UpdateFundingModal />
                <AddFundingModal />
                <UpdateFootprintModal />
                <AddFootprintModal />
                <JobModal/>
                <MemberModal/>
                <AddCompsModal />
                <DecisionModal />
                <CollectionFilterModal />

            </div>
        )
    }
});


module.exports = ModalList;
