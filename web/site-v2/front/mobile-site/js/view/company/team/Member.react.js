var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var MemberStore = require('../../../../../webapp-site/js/store/company/MemberStore');
var MemberActions = require('../../../../../webapp-site/js/action/company/MemberActions');
var CompanyUtil = require('../../../../../webapp-site/js/util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var DivExtend = require('../../../../../react-kit/basic/DivExtend.react');

const Member = React.createClass({
    mixins: [Reflux.connect(MemberStore, 'data')],

    componentWillMount() {
        MemberActions.get(this.props.id);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.id == nextProps.id) return;
        MemberActions.get( nextProps.id);
    },

    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;

        var data = state.data.list;
        if(data.length ==0) return null;

        var showAll = this.state.data.showAll;

        var more;
        var len = 3;
        if(data.length > len){
            data = CompanyUtil.getSubList(data, len, showAll);
            if(showAll){
                more = <DivExtend type="less" extend={this.extend}/>
            }
            else{
                more = <DivExtend type="more" extend={this.extend}/>
            }
        }

        return (
            <div className="section">
                <span className="section-header">
                    核心成员
                </span>
                <section className="section-body">
                    {
                        data.map(function (result, index) {
                            if (result.member == null) {
                                return null
                            } else {
                                return <MemberItem key={index} data={result}/>;
                            }
                        })
                    }

                    {more}

                </section>
            </div>

        )
    },

    extend(){
        MemberActions.showAll();
    }

});

const MemberItem = React.createClass({
    render(){
        var item = this.props.data;
        var photo = "";
        if(item.member.photo != null){
            photo = "/file/" + item.member.photo;
        }else{
            photo = "/resources/image/photo_default.png"
        }

        return (
            <div className="member">
                <div className="member-basic">
                    <img className="member-photo" src={photo}/>
                    <div className="member-info">
                        <div className="member-name">
                            <strong>{item.member.name}</strong>
                        </div>
                        <div className="member-position">
                            {item.companyMemberRel.position}
                        </div>
                        <div className="member-education">
                            {item.member.education}
                        </div>
                        <div className="member-work">
                            {item.member.work}
                        </div>
                    </div>
                </div>

            </div>

        )
    },

});


module.exports = Member;