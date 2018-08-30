var React = require('react');
var $ = require('jquery');

var NewMemberStore = require('../../store/member/NewMemberStore');
var Functions = require('../../util/Functions');


var LastMember = React.createClass({

    getInitialState() {
        return {data:NewMemberStore.get().last};
    },

    componentDidMount() {
        NewMemberStore.addChangeListener(this._onChange);
    },
    componentWillUnmount(){
        NewMemberStore.removeChangeListener(this._onChange);
    },

    render: function(){
        var data = this.state.data;
        if (data.id == -1){
            return(
                <div className="right-part">
                    <div>
                        <div className="source-list">
                            <div className="source-info">
                                <div className="source-head">
                                    <label>无新增加记录</label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }else{
            //console.log(state);
            return(
                <div className="right-part">
                    <div>
                        <div className="source-list">
                            <div className="source-info">
                                <div className="source-head">
                                    <label>新增加记录</label>
                                </div>
                                <div className="source-detail">
                                    <div>ID: {data.id}</div>
                                    <div>姓名: {data.name}</div>
                                    <div>教育: {data.education}</div>
                                    <div>工作: {data.work}</div>
                                    <div>工作重点: {data.workEmphasis}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )
        }
    },

    _onChange() {
        var store = NewMemberStore.get();
        //console.log("Last Member _onChange()");
        //console.log(store);
        if (store != null)
            this.setState({data: store.last});
    },

});

module.exports = LastMember;