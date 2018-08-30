var React = require('react');
var $ = require('jquery');


var SourceActionUtil = require('../../../action/source/SourceActionUtil');
var SourceMemberAction = require('../../../action/source/SourceMemberAction');
var SourceMemberStore = require('../../../store/source/SourceMemberStore');
var Functions = require('../../../util/Functions');

var PropsSetOrChangeMixin = {
    componentWillMount: function() {
        this.onPropsSetOrChange(this.props.id);
    },

    componentWillReceiveProps: function(nextProps) {
        this.onPropsSetOrChange(nextProps.id);
    }
};


var SourceMember = React.createClass({

    mixins: [PropsSetOrChangeMixin],

    onPropsSetOrChange(id){
        SourceMemberAction.get(id);
    },

    componentDidMount(){
        SourceMemberStore.addChangeListener(this._onChange);
    },

    componentWillUnmount(){
        SourceMemberStore.removeChangeListener(this._onChange);
    },

    render: function(){
        var state = this.state;
        if (state == null){
            return(<div></div>)
        }else{
            //console.log(state);
            return(
                <div className="right-part">
                    <div>
                        <div className="source-list">
                            { this.state.data.map(function(result){
                                var img="";
                                if(result.member.photo != null){
                                    img = <img src={"/file/" + result.member.photo} width="100"/>
                                }
                                source = SourceActionUtil.getSourceInfo(result.member.source,result.member.sourceId)
                                types = Functions.memberTypeSelect();
                                //console.log(types)
                                typeName = "";
                                for(var i in types){
                                    if( types[i].value == result.rel.type ){
                                        typeName = types[i].name;
                                        break
                                    }
                                }
                                return(
                                    <div className="source-info">
                                        <div className="source-detail">
                                            <div>源: {source.sourceName}</div>
                                            <div>源Url: <a href={source.sourceMemberUrl} target="_blank">{source.sourceMemberUrl}</a></div>
                                            <div>姓名: {result.member.name}</div>
                                            <div>职位: {result.rel.position}</div>
                                            <div>成员类型: {typeName}</div>
                                            <div>照片: {img}</div>
                                            <div>微博: {result.member.weibo}</div>
                                            <div>地区: {result.member.location}</div>
                                            <div>角色: {result.member.role}</div>
                                            <div>教育: {result.member.education}</div>
                                            <div>工作: {result.member.work}</div>
                                            <div>描述: {result.member.description}</div>
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

    _onChange() {
        var store = SourceMemberStore.get();
        if (store != null)
            this.setState({data: store});
    },

});

module.exports = SourceMember;