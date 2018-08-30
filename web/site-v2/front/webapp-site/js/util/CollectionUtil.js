const CollectionUtil = {

    teamBackgroundSelect: [{name: '985', value: 42010},
        {name: '211', value: 42020},
        {name: 'BAT', value: 43010},
        {name: '知名互联网企业', value: 43020},
        {name: '世界500强', value: 43030}],

    investorSelect: [{name: '知名投资机构', value: 44010}],

    dateSelect(){
        var date = new Date().getFullYear();
        var dateSelect = [];
        for (var i = 0; i < 5; i++) {
            dateSelect.push({name: date, value: date});
            date -= 1;
        }
        return dateSelect;
    },


    selected(data, list){
        var flag = false;
        for (var i in list) {
            if (list[i].name == data.name) {
                flag = true;
                list.splice(i, 1);
            }
        }

        if (!flag) list.push(data);


        return list;
    },

    isSelected(data, list){
        for (var i in list) {
            if (list[i].name == data.name)
                return true;
        }
        return false;
    },

    listAddUnique(list, item){
        var flag = false;
        if (list.length == 0) {
            list.push(item);
        }
        else {
            for (var i in list) {
                if (list[i].value == item.value) {
                    flag = true;
                }
            }

            if (!flag) list.push(item);
        }

        return list;
    },

    countDateDiff(updateTime){

        var currentTime = new Date();
        var oldTime = new Date(updateTime);
        var diff = currentTime.getTime() - oldTime.getTime();
        //天数
        var days = Math.floor(diff / (24 * 3600 * 1000));
        //计算天数后剩余的毫秒数
        var diff1 = diff % (24 * 3600 * 1000);
        var hours = Math.floor(diff1 / (3600 * 1000));
        //计算相差分钟数
        var diff2 = diff1 % (3600 * 1000);       //计算小时数后剩余的毫秒数
        var minutes = Math.floor(diff2 / (60 * 1000));
        ////计算相差秒数
        //var diff3=diff2%(60*1000);    //计算分钟数后剩余的毫秒数
        //var seconds=Math.round(diff3/1000);
        var time;
        if (days > 0) {
            time = oldTime.format("yyyy-MM-dd hh:mm:ss").substring(0,10);
        }
        if (days == 0 && hours > 0) {
            time = hours + "小时前";
        }
        if (days == 0 && hours == 0 && minutes > 0) {
            time = minutes + "分钟前";
        }
        if (days == 0 && hours == 0 && minutes == 0) {
            time = "刚刚";
        }
        return time;
    },

    isLoading(store){
        if (store.loading) return true;
        var len;
        if (store.timeline == null) {
            len=0;
        }else{
            len=store.timeline.length;
        }
        if (store.timelineTotal > len) {
            return false;
        }
        else if (store.timelineTotal > 0) {
            return true;
        }
        return false;
    },

    getLoadParam(store){
        var start;
        var url = "/api/company/collection/";
        if (store.collectionId) {
            url += "compList";
        } else {
            url += "timeLineList";
        }
        if(store.timeline==null){
            start=0
        }
        else{
            start = store.timeline.length;
        }

        return {start: start, url: url};
    },

    setResult(result, store){
        var list = result.list;
        if (store.timeline == null) {
            store.timeline = [];
        }
        store.timeline = store.timeline.concat(list);
        if (store.collectionId) {
            store.collection = result.collection;
        }
        return store;
    },

    changeScore(score, code, list){
        for (var i in list) {
            var item = list[i];
            if (code == item.company.code) {
                item.score = score;
            }
        }
    },

    getSysColsId(list){
        var faId;
        for (var i in list) {
            if (list[i].type == 39010) {
                faId == list[i].id;
                break;
            }
        }
        return faId;
    },

    followCollection(id,store){
        var hotCols = store.hotCols;
        for(var i in hotCols){
            if(hotCols[i].id==id){
                hotCols[i].active='Y';
            }
        }
    },

    unFollowCollection(id,store){
        var hotCols = store.hotCols;
        for(var i in hotCols){
            if(hotCols[i].id==id){
                hotCols[i].active='N';
            }
        }
    }

};

module.exports = CollectionUtil;