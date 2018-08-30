var Functions = require('../../../react-kit/util/Functions');
const OrgUtil = {
    newOrg(){
        return {
            name: "",
            //组织
            type: 17020,
            //默认x联盟
            status: 31010,
            //机构等级
            grade: 33020
        }
    },
    newUser(){
        return {
            id:null,
            username: '',
            email: '',
            password: ''
        }

    },
    roleType: [
        {name: '公司管理员', value: 25010},
        {name: '创业者', value: 25020},
        {name: '投资-合伙人', value: 25030},
        {name: '投资-投资经理', value: 25040},
        {name: '投资-其他', value: 25050},
        {name: '后台管理员', value: 25060},
        {name: '数据维护', value: 25070},
        {name: '其他', value: 25080}
    ],

    getRoles(list){
        var roles = [];
        if (list.length > 0) {
            for (var i in list) {
                if (list[i].selected) {
                    roles.push(list[i].value);
                }
            }
        }
        return roles;
    },

    isLoading(store){
        if (store.loading) return true;
        if (store.totalUser > store.userList.length)return false;

    },

    parseRole(role){
        var name;
        switch (Number(role)){
            case  25010 :name='公司管理员';break;
            case  25020 :name='创业者';break;
            case  25030 :name='投资-合伙人';break;
            case  25040 :name='投资-投资经理';break;
            case  25050 :name='投资-其他';break;
            case  25060 :name='后台管理员';break;
            case  25070 :name='数据维护';break;
            case  25080 :name='其他';break;
            default :break;
        }
        return name;
    }
};
module.exports = OrgUtil;
