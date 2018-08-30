var Functions = require('../../../react-kit/util/Functions')
const ColdCallUtil = {

    getTypeNum(typeName){
        var no;
        switch (typeName) {
            case 'unmatch':no = 0;break;
            case 'match':no = 1;break;
            default :no = 0;break;
        }
        return no;
    },

    getLoadParam(type,store){
        var start=0;
        var url = "/api/admin/coldCall/";
        switch (Number(type)) {
            case 0:
                url += "unmatch";
                start=store.unmatched_list.length;
                break;
            case 1:
                url += "match";
                start=store.matched_list.length;
                break;
            default :start = 0;url += "unmatch";break;
        }
        return {start: start, url: url};
    },

    setResult(type, result, store){
        var list = result.list;
        switch (Number(type)) {
            case 0:
                store.unmatched_list = store.unmatched_list.concat(list);
                store.list_coldcall = Functions.clone(store.unmatched_list);
                break;
            case 1:
                store.matched_list = store.matched_list.concat(list);
                store.list_coldcall = Functions.clone(store.matched_list);
                break;
            default :
                break;
        }

        return store;
    },
    isLoading(type, store){
        if(store.loading) return true;
        switch (Number(type)) {
            case 0:
                if(store.unmatch_total > store.unmatched_list.length)
                    return false;
                else if(store.unmatch_total > 0){
                    return true;
                }
                break;
            case 1:
                if(store.match_total > store.matched_list.length)
                    return false;
                else if(store.match_total > 0){
                    return true;
                }
                break;
            default :
                break;
        }
        return false;
    }
};

module.exports = ColdCallUtil;

