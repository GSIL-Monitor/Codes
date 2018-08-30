var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var Functions = require('../../../../../react-kit/util/Functions');
var OrgStore = require('../../../store/OrgStore');
var OrgActions = require('../../../action/OrgActions');
var OrgUtil = require('../../../util/OrgUtil');
var RoleTypeItem = require('../form/RoleTypeItem.react');
var FormInput = require('../../../../../webapp-site/js/view/company/create/form/FormInput.react');

const UserInfoContent = React.createClass({
    mixins: [Reflux.connect(OrgStore, 'data')],

    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;
        var updateUser  = this.state.data.updateUser;
        if(Functions.isEmptyObject(updateUser)) return null;
        var roleType = OrgUtil.roleType;
        var roleList = this.state.data.modalRoles;
        var me =this;
        return (
            <div className="main-body">
                <FormInput className='form-input-short'
                           label='用户名称'
                           name='username'
                           value={updateUser.username}
                           onChange={this.change}
                           required={true}
                           user={true}
                    />
                <FormInput className='form-input-short'
                           label='邮件地址'
                           name='email'
                           value={updateUser.email}
                           onChange={this.change}
                           required={true}
                           user={true}
                           onBlur={this.blur}
                    />

                <div className='create-company-form'>
                    <div className='cc-form-left org-user-left'>
                        <div className='user-role-label'>用户角色</div>
                    </div>
                    {roleType.map(function (result) {
                        return <RoleTypeItem key={result.value} data={result} modal={true} roleList={roleList} onClick={me.click}/>
                    })}
                </div>
                <div className="org-user-update">
                    <button className="btn btn-navy " onClick={this.update}>更新</button>
                </div>
            </div>
        )

    },

    change(e){
        OrgActions.updateOrgUser(e.target.name, e.target.value);
    },
    update(){
        OrgActions.updateUser();
    },
    click(value){
        OrgActions.selectType(value,true);
    },
    blur(){
        if(this.state.data.oldUser.email==this.state.data.updateUser.email){
            return;
        }
        OrgActions.getUserByEmail(true)
    }

});
module.exports = UserInfoContent;


