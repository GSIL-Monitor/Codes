var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SourceActionUtil = require('../../../action/source/SourceActionUtil');
var SourceMemberStore = require('../../../reflux/SourceMemberStore');
var SourceMemberActions = require('../../../reflux/SourceMemberActions');

var SourceMember = React.createClass({
    mixins: [Reflux.connect(SourceMemberStore, 'members')],
    getInitialState: function () {
        return {members: null};
    },
    componentDidMount: function () {
        SourceMemberActions.get(this.props.id);
    },

    render: function(){
        var state = this.state;
        if (state == null || state["members"] == null){
            return(<div>无源数据</div>)
        }else{
            //console.log(state);
            var members = state["members"];
            return(
                <div className="right-part">
                    <div>
                        <div className="source-list">
                        { members.map(function(member) {
                            var img = "";
                            if (member.photo != null) {
                                img = <img src={"/file/" + member.photo} width="100"/>
                            }

                            source = SourceActionUtil.getSourceInfo(member.source, member.sourceId)

                            return (
                            <div className="source-info">
                                <div className="source-detail">
                                    <div>源: {source.sourceName}</div>
                                    <div>源Url: <a href={source.sourceMemberUrl}
                                                  target="_blank">{source.sourceMemberUrl}</a></div>
                                    <div>姓名: {member.name}</div>
                                    <div>照片: {img}</div>
                                    <div>微博: {member.weibo}</div>
                                    <div>地区: {member.location}</div>
                                    <div>角色: {member.role}</div>
                                    <div>教育: {member.education}</div>
                                    <div>工作: {member.work}</div>
                                    <div>描述: {member.description}</div>
                                </div>
                            </div>
                            )
                        })}
                        </div>
                    </div>
                </div>
            )
        }
    },

});

module.exports = SourceMember;