var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var OrgStore = require('../../store/OrgStore');
var OrgActions = require('../../action/OrgActions');
var ValidateActions = require('../../action/validation/ValidateOrgActions');
var ValidateStore = require('../../store/validation/ValidateOrgStore');
var Functions = require('../../../../react-kit/util/Functions');
var FormInput = require('../../../../webapp-site/js/view/company/create/form/FormInput.react');
var OrgUtil = require('../../util/OrgUtil');
var View = require('../../../../react-kit/util/View');

var RoleTypeItem = require('./form/RoleTypeItem.react')

const NewOrg = React.createClass({

    mixins: [Reflux.connect(OrgStore, 'data')],

    componentWillMount() {
        OrgActions.getInitUsersInfo(this.props.id);
    },
    componentWillReceiveProps(nextProps) {
        OrgActions.getInitUsersInfo(nextProps.id);
    },
    //componentDidMount(){
    //    window.addEventListener('scroll', this.scroll);
    //},
    //
    //componentWillUnmount(){
    //    window.removeEventListener('scroll', this.scroll);
    //},


    render(){
        if (Functions.isEmptyObject(this.state)) return null;

        var orgName = this.state.data.orgName;
        var userList = this.state.data.userList;
        var orgId = this.state.data.orgId;
        var roleType = OrgUtil.roleType;
        var roleList = this.state.data.roles;
        var user = this.state.data.user;
        var me = this;
        var add = '新增用户';
        if (this.state.data.create) {
            add = '创建中...'
        }

        var usersInfo;
        if (userList == null || userList.length == 0) {
            usersInfo = "";
        }
        else {
            usersInfo = <div className="dd-score-list">
                <div className="preScore-item  dd-list-head">
                    <div className="preScore-item-rank">序号</div>
                    <div>用户名</div>
                    <div>邮箱</div>
                    <div>时间</div>
                    <div>角色</div>
                    <div>修改</div>
                </div>
                {userList.map(function (result, index) {
                    return <UserItem key={index}
                                     index={index}
                                     data={result}
                                     orgId={orgId}
                        />
                })}


            </div>
        }

        return (
            <div className="main-body">

                <h3 className="cc-org-title ">{orgName}</h3>

                <FormInput className='form-input-short'
                           label='用户名称'
                           name='username'
                           value={user.username}
                           onChange={this.change}
                           required={true}
                           user={true}
                    />
                <FormInput className='form-input-short'
                           label='邮件地址'
                           name='email'
                           value={user.email}
                           onChange={this.change}
                           required={true}
                           user={true}
                           onBlur={this.blur}
                    />
                <FormInput className='form-input-short'
                           label='用户密码'
                           name='password'
                           value={user.password}
                           onChange={this.change}
                           required={true}
                           user={true}
                    />

                <div className='create-company-form'>
                    <div className='cc-form-left org-user-left'>
                        <div className='user-role-label'>用户角色</div>
                    </div>
                    {roleType.map(function (result) {
                        return <RoleTypeItem key={result.value} data={result} roleList={roleList} onClick={me.click}/>
                    })}
                </div>
                <div className="org-user-add">
                    <button className="btn btn-navy " onClick={this.create}>{add}</button>
                </div>

                <div>
                    {usersInfo}
                </div>
            </div>
        )
    },

    change(e){
        OrgActions.user(e.target.name, e.target.value, 'email');
    },

    create(){
        OrgActions.addUser(this.state.data.orgId);

    },

    blur(){
        OrgActions.getUserByEmail()
    },

    //scroll(){
    //    if (View.bottomLoad(100)) {
    //        OrgActions.listMore(this.state.data.orgId);
    //    }
    //},

    click(value){
        OrgActions.selectType(value);
    }

});

const UserItem = React.createClass({
    render(){
        var index = this.props.index + 1;
        var data = this.props.data;
        var roles = data.roles;
        var role = '';
        if (null != roles && roles.length > 0) {
            for (var i in roles) {
                role += OrgUtil.parseRole(roles[i]) + ','
            }
            role = role.substring(0, role.length - 1);
        }
        else role = 'N/A';
        var time = data.createTime;
        var createTime = new Date(time).format("yyyy-MM-dd hh:mm:ss");
            return (
                <div className="preScore-item">
                    <div className="preScore-item-rank">{index}</div>
                    <div>{data.username}</div>
                    <div>{data.email}</div>
                    <div>{createTime.substring(0, 10)}</div>
                    <div>{role}</div>
                    <div>
                        <a onClick={this.update}>
                            <i className="fa fa-pencil-square-o"></i>
                        </a>
                    </div>
                </div>
            )
    },

    update(){
            OrgActions.cloneUser(this.props.data);
        }

    //delete(){
    //    OrgActions.deleteUser(this.props.data.id,this.props.orgId)
    //},

    //confirm(){
    //    OrgActions.updateUser(this.props.orgId);
    //
    //}
});

module.exports = NewOrg;

