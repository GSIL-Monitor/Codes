var Reflux = require('reflux');
var $ = require('jquery');
var OrgActions = require('../action/OrgActions');
var Functions = require('../../../react-kit/util/Functions');
var Http = require('../../../react-kit/util/Http');
var ValidateStore = require('./validation/ValidateOrgStore');
var OrgUtil = require('../util/OrgUtil');

const OrgStore = Reflux.createStore({
    store: {
        org: OrgUtil.newOrg(),
        add: false,
        orgList: null,
        newOrg: null,
        updateOrg: null,
        totalUser:null,
        userList:[],
        orgId:null,
        orgName:null,
        user: OrgUtil.newUser(),
        updateUser: null,
        oldUser:null,
        create: false,
        exitsUser: false,
        modifyId: null,
        roles: [],
        pageSize: 3,
        loading:false,
        //记录修改user时候，选的用户角色
        modalRoles:[]
    },

    init: function () {
        this.listenToMany(OrgActions);
    },

    onGetInitData(){
        this.getOrgList();
    },

    onGetInitUsersInfo(id){
        this.store.orgId=id;
        this.store.userList=[];
        this.countUser(id);
        this.onListMore(id);
        this.trigger(this.store);
    },

    onChange(name, value){
        this.store.org[name] = value;
        this.trigger(this.store);
    },

    onUpdateOrg(name, value){
        this.store.updateOrg[name] = value;
        this.trigger(this.store);
    },

    onAdd(){
        //未校验完成不予创建
        if (ValidateStore.store.name.hint != 'usable') {
            return;
        }
        //名称存在不予创建
        if (!ValidateStore.store.name.validation) {
            $("#orgName").focus();
            return;
        }
        this.store.add = true;
        this.trigger(this.store);
        this.store.org.name = this.store.org.name.trim();
        var payload = {payload: {org: this.store.org}};
        var url = "/api/admin/org/add";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.org = OrgUtil.newOrg();
                this.store.add = false;
                window.location.href = "/admin/#/org";
            }
            else {
                $('.hint').html('新增失败!').show().fadeOut(3000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    getOrgList(){
        var payload = {payload: null};
        var url = "/api/admin/org/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.orgList = result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);

    },

    onDeleteOrg(id){
        var payload = {payload: {id: id}};
        var url = "/api/admin/org/delete";
        var callback = function (result) {
            if (result.code == 0) {
                this.getOrgList();
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onCloneOrg(data){
        this.store.updateOrg = Functions.clone(data);
        this.trigger(this.store);
    },

    onConfirm(){
        var payload = {payload: {org: this.store.updateOrg}};
        var url = "/api/admin/org/update";
        var callback = function (result) {
            if (result.code == 0) {
                $('.hint').html('更新成功!').show().fadeOut(3000);
                this.getOrgList();
                this.cleanOrg();
            }
            else {
                $('.hint').html('更新失败!').show().fadeOut(3000);
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onListMore(id){
        var payload = {payload: { id: id}};
        var url = "/api/admin/org/usersInfo";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.userList=result.list;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    //onListMore(id){
    //    if(OrgUtil.isLoading(this.store)) return;
    //    this.store.loading = true;
    //    var payload = {payload: { id: id,
    //                              pageSize: this.store.pageSize,
    //                              from: this.store.userList.length}};
    //    var url = "/api/admin/org/usersInfo";
    //    var callback = function (result) {
    //        if (result.code == 0) {
    //            this.store.loading = false;
    //            this.store.userList=this.store.userList.concat(result.list);
    //        }
    //        this.trigger(this.store);
    //    }.bind(this);
    //
    //    Http.ajax(payload, url, callback);
    //},

    onUser(name, value, email){
        this.store.user[name] = value;
        if (email) {
            this.store.exitsUser = false;
        }
        this.trigger(this.store);
    },

    onAddUser(id){
        if (this.store.exitsUser) {
            $('.hint').html('邮件地址已存在!').show().fadeOut(3000);
            return;
        }
        if (this.store.user.username.trim() == '') {
            $('.hint').html('用户名必填!').show().fadeOut(3000);
            return;
        }
        if (this.store.user.email.trim() == '') {
            $('.hint').html('邮件地址必填!').show().fadeOut(3000);
            return;
        }
        if (this.store.user.password.trim() == '') {
            $('.hint').html('用户密码必填!').show().fadeOut(3000);
            return;
        }

        this.store.create = true;
        this.trigger(this.store);
        this.store.user.username = this.store.user.username.trim();
        this.store.user.email = this.store.user.email.trim();
        this.store.user.password = this.store.user.password.trim();
        var payload = {
            payload: {
                id: id,
                user: this.store.user,
                roles: OrgUtil.getRoles(this.store.roles)
            }
        };
        var url = "/api/admin/org/user/add";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.user = OrgUtil.newUser();
                this.store.roles = [];
                this.store.exitsUser=false;
                this.store.create = false;
                $('.hint').html('新增成功!').show().fadeOut(3000);
                this.onListMore(id);
            }
            else {
                $('.hint').html('新增失败!').show().fadeOut(3000);
                this.store.create = false;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);

    },

    onDeleteUser(id, orgId){
        var payload = {payload: {id: id, orgId: orgId}};
        var url = "/api/admin/org/user/delete";
        var callback = function (result) {
            if (result.code == 0) {
                $('.hint').html('删除成功!').show().fadeOut(3000);
                this.onGetOrgData(orgId);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onCloneUser(data){
        this.store.modalRoles=[];
        this.store.updateUser = Functions.clone(data);
        this.store.oldUser = data;
        var roles = data.roles;
        for(var i in  roles){
            this.store.modalRoles.push({value: roles[i], selected: true});
        }
        this.trigger(this.store);
        $('#userInfo').show();

    },

    onUpdateOrgUser(name, value){
        this.store.updateUser[name] = value;
        this.trigger(this.store);
    },

    onUpdateUser(){
        if (this.store.exitsUser) {
            $('.hint').html('邮件地址已存在!').show().fadeOut(3000);
            return;
        }
        var updateUser = this.store.updateUser;
        var user = OrgUtil.newUser();
        user.id=updateUser.userId;
        user.username=updateUser.username.trim();
        user.email=updateUser.email.trim();
        var payload = {payload: {user: user,roles:OrgUtil.getRoles(this.store.modalRoles)}};
        var url = "/api/admin/org/user/update";
        var callback = function (result) {
            if (result.code == 0) {
                this.onListMore(this.store.orgId);
                this.store.exitsUser=false;
                $('#userInfo').hide();
                $('.hint').html('更新成功!').show().fadeOut(3000);
            }
            else {
                $('.hint').html('更新失败!').show().fadeOut(3000);
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetUserByEmail(update){
        var email = update?this.store.updateUser.email:this.store.user.email;
        var payload = {payload: {email: email.trim()}};
        var url = "/api/admin/org/user/get";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.exitsUser = result.exit;
                if (this.store.exitsUser) {
                    $('.hint').html('邮件地址已存在!').show().fadeOut(3000);
                }
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onModify(id, org){
        if (this.store.modifyId == null) {
            this.store.modifyId = id;
            this.onCloneOrg(org);
        }
        else if (this.store.modifyId != id) {
            $('.hint').html('请先完成当前修改!').show().fadeOut(3000);
        }
        this.trigger(this.store);
    },

    onCancel(){
        this.cleanOrg();
    },

    cleanOrg(){
        this.store.modifyId = null;
        this.store.updateOrg = null;
        this.trigger(this.store);
    },

    onSelectType(value,modal){
        var roles = modal?this.store.modalRoles:this.store.roles;
        var role = {value: value, selected: true};
        if (roles.length == 0) {
            roles.push(role);
        }
        else {
            var flag = false;
            for (var i in roles) {
                if (value == roles[i].value) {
                    flag = true;
                    if (roles[i].selected) {
                        roles[i].selected = false;
                    }
                    else {
                        roles[i].selected = true;
                    }
                }
            }
            if (!flag) roles.push(role);
        }
        this.trigger(this.store);
    },

    countUser(id){
        var payload = {payload:{id: id}};
        var url = "/api/admin/org/countUser";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.totalUser = result.totalUser;
                this.store.orgName = result.orgName;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    }

});

module.exports = OrgStore;