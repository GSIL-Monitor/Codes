const TaskUtil = {
    getTypeNum(typeName){
        var no;
        switch (typeName) {
            case 'self':
                no = 23010;
                break;
            case 'coldcall':
                no = 23020;
                break;
            case 'recommend':
                no = 23030;
                break;
            case 'publish':
                no = 2;
                break;
            default :
                no = 23020;
                break;
        }
        return no;
    },

    getTypeName(typeName){
        var name;
        switch (typeName) {
            case 23010:
                name = 'self';
                break;
            case 23020:
                name = 'coldcall';
                break;
            case 23030:
                name = 'recommend';
                break;
            case 2:
                name = 'publish';
                break;
            default :
                name = 'coldcall';
                break;
        }
        return name;
    },

    isLoading(type, store){
        if(store.loading) return true;
        if(!store.firstLoad) return false;
        switch (Number(type)) {
            case 23010:
                if(store.cnt_total_self == store.list_self.length)
                    return true;
                break;
            case 1:
                if(store.cnt_total_task == store.list_task.length)
                    return true;
                break;
            case 2:
                if(store.cnt_total_sponsoredcoldcall == store.list_sponsoredcoldcall.length)
                    return true;
                break;
            default :
                break;
        }
        return false;
    },

    getLoadParam(type, store){
        var start;
        var url = "/api/company/mytask/";
        var filter = 0;

        switch (Number(type)) {
            case 23010:
                start = store.list_self.length;
                url += "self/list";
                filter = store.filter_self;
                break;
            case 1:
                start = store.list_task.length;
                filter = store.filter_task;
                url += 'task/list';
                break;
            case 2:
                start = store.list_sponsoredcoldcall.length;
                filter = store.filter_sponsoredcoldcall;
                url += 'publish/list';
                break;
            default :
                start = 0;
                break;

        }

        return {start: start, url: url, type: store.filter_task_type, filter:filter};
    },

    setResult(type, result, store){
        var list = result.list;
        switch (Number(type)) {
            case 23010:
                store.cnt_total_self = result.cnt_total;
                store.list_self = store.list_self.concat(list);
                break;
            case 1:
                store.cnt_total_task = result.cnt_total;
                store.list_task = store.list_task.concat(list);
                break;
            case 2:
                store.cnt_total_sponsoredcoldcall = result.cnt_total;
                store.list_sponsoredcoldcall = store.list_sponsoredcoldcall.concat(list);
                break;
            default :
                break;

        }

        return store;
    },


    getScoreName(value){
        var name;
        switch (Number(value)) {
            case 1:
                name = '不关心';
                break;
            case 2:
                name = '太烂了';
                break;
            case 3:
                name = '随便聊聊';
                break;
            case 4:
                name = '重点跟进';
                break;
            default :
                name ='待处理';
                break;

        }

        return name;
    },

    getDeclineName(value){
        var name;
        switch (Number(value)) {
            case 32010:
                name = '项目阶段不符';
                break;
            case 32020:
                name = '不是我的关注领域';
                break;
            case 32030:
                name = '已经看过了';
                break;
            case 32040:
                name = '太烂了';
                break;
            default :
                name ='';
                break;

        }

        return name;
    }

};

module.exports = TaskUtil;