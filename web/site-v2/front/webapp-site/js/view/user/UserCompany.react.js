var React = require('react');
var ReactDom = require('react-dom');
var Reflux = require('reflux');
var $ = require('jquery');

var UserCompanyStore = require('../../store/UserCompanyStore');
var UserCompanyActions = require('../../action/UserCompanyActions');
var Functions = require('../../../../react-kit/util/Functions');
var NoteUtil = require('../../util/NoteUtil');

var Score = require('./company/Score.react');
var Note = require('./company/Note.react');
var Coldcall = require('./company/Coldcall.react');

const UserCompany = React.createClass({

    mixins: [Reflux.connect(UserCompanyStore, 'data')],

    componentWillMount() {
        UserCompanyActions.init(this.props.code);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.code == nextProps.code) return;
        UserCompanyActions.init(nextProps.code);
    },


    render() {
        if (Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;

        return (
            <div className="user-operate">
                <Score score={data.score}
                       scores={data.scores}
                    />
                <Note   notes={data.notes}
                        noteText={data.noteText}
                    />

                <Coldcall data={data}/>
            </div>
        )
    }

});






module.exports = UserCompany;

