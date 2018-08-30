var React = require('react');

var UserScoreModal = require('../user/company/UserScoreModal.react');
var DemodayScoreModal = require('../demoday/score/modal/ScoreModal.react');
var SearchFilterModal = require('../../../../webapp-search/js/view/search/modal/MobileFilterModal.react');

var ModalList= React.createClass({
    render(){
        return(
            <div>
                <UserScoreModal />
                <DemodayScoreModal />
                <SearchFilterModal />
            </div>
        )
    }
});


module.exports = ModalList;
