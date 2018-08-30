var React = require('react');
var DemodayMoal = require('../demoDay/modal/DemodayModal.react');
var RejectOrgListModal=require('../demoDay/modal/RejectOrgListModal.react');
var OrgPreScoresModal = require('../demoDay/modal/PreScoresModal.reat.js');
var UserInfoModal = require('../org/modal/UserInfoModel.react');

var ModalList = React.createClass({
    render(){
        return (
            <div>

                <DemodayMoal />
                <RejectOrgListModal />
                <OrgPreScoresModal />
                <UserInfoModal />
            </div>
        )
    }
});


module.exports = ModalList;
