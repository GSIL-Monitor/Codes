var React = require('react');
var $ = require('jquery');


// view
var FormInput = require('../form/FormInput.react');
var FormTextarea = require('../form/FormTextarea.react');
var FormSelect = require('../form/FormSelect.react');

var ActionUtil = require('../../action/ActionUtil');
var MemberAction = require('../../action/MemberAction');
var MemberStore = require('../../store/MemberStore');
var MemberForm = require('./MemberForm.react');
var SourceMember = require('./source/SourceMember.react');


const Member = React.createClass({

    getInitialState() {
        return {idx:0};
    },
    componentDidMount() {
        MemberAction.get(this.props.id);
        MemberStore.addChangeListener(this._onChange);
    },
    componentWillUnmount(){
        MemberStore.removeChangeListener(this._onChange);
    },
    render() {
        $('.nav-c > ul > li:eq(3) > a').css('color', '#1c84c6');

        if (this.state.members == null){
            return (
                <nav></nav>
            )
        }else {
            var idx = -1;
            return (
                <div>
                    <nav className="nav-list">
                        <ul>
                            { this.state.members.map(function (result) {
                                idx++;
                                return <NavDetail idx={idx} key={idx} data={result} navClick={this.handleClick}/>;
                            }.bind(this))}
                        </ul>
                    </nav>
                    <div className="m-t-10 ">
                        <a className="a-button right" onClick={this.addClick}>添加记录</a>
                    </div>
                    <div className="m-t-10">
                        <div className="left-part">
                            <MemberForm data={this.state.member} onChange={this.handleChange}/>
                        </div>
                        <SourceMember id={this.state.member.rel.id} />
                    </div>
                </div>
            )
        }
    },

    handleChange(event){
        //console.log(this.state.member);
        MemberAction.change(this.state.member.member.id, event.target.name, event.target.value);
    },

    handleClick(idx){
        MemberAction.chooseMember(idx);
    },

    addClick(){
        //MemberAction.addCompanyMemberRel();
    },

    _onChange() {
        this.setState({
            members: MemberStore.get().members,
            idx:MemberStore.get().idx,
            member:MemberStore.get().members[MemberStore.get().idx]
        });
    }

});


const NavDetail =  React.createClass({

    render(){
        var data = this.props.data;
        var idx = this.props.idx;

        return (
            <li onClick={this.handleClick} className={idx==MemberStore.get().idx?'selected':''}>
                <h3>{data.member.name}</h3>
                <p>{data.rel.position} </p>
            </li>
        )
    },

    handleClick(event){
        this.props.navClick(this.props.idx);
    }

});





module.exports = Member;

