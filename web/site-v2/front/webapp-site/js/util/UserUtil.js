var Http = require('../../../react-kit/util/Http');
var $ = require('jquery');

const UserUtil = {

    initSectors(){
        var sectors = [
            {id: 1, name:'电子商务' },
            {id: 2, name:'本地生活' },
            {id: 3, name:'社交' },
            {id: 4, name:'智能硬件' },
            {id: 5, name:'汽车交通' },
            {id: 6, name:'医疗健康' },
            {id: 7, name:'金融' },
            {id: 8, name:'企业服务' },
            {id: 9, name:'工具软件' },
            {id: 10, name:'旅游户外' },
            {id: 11, name:'教育' },
            {id: 12, name:'房产家装' },
            {id: 13, name:'游戏' },
            {id: 14, name:'文化娱乐' },
            {id: 15, name:'运动健身' },
            {id: 16, name:'广告营销' },
            {id: 17, name:'餐饮' },
            {id: 18, name:'B2B' },
            {id: 19, name:'农业' },
            {id: 999, name:'其他' }
        ];

        return sectors;
    },

    isSame(sectors, oldSectors){
        if(sectors.length != oldSectors.length) return false;
        for(var i in sectors){
            var flag = false;
            for(var k in oldSectors){
                if(sectors[i] == oldSectors[k]){
                    flag = true;
                }
            }
            if(!flag) return false;
        }
        return true;
    },


    listChange(value, list){
        var flag = false;
        if(list.length == 0){
            list.push(value.id);
        }else{
            for(var i in list){
                if(list[i] == value.id){
                    list.splice(i, 1);
                    flag = true;
                }
            }


            if(!flag) {
                list.push(value.id);
            }
        }

        return list;
    },

    getNewIds(update, old){
        var newIds = [];
        for(var i in update){
            var newFlag = true;

            for(var k in old){
                if(update[i] == old[k]) newFlag = false;
            }

            if(newFlag) {
                newIds.push(update[i]);
            }
        }
        return newIds;
    },

    getDeleteIds(update, old){
        var deleteIds = [];
        for(var i in old){
            var deleteFlag = true;
            for(var k in update){
                if(old[i] == update[k]) deleteFlag = false;
            }

            if(deleteFlag) deleteIds.push(old[i]);
        }
        return deleteIds;
    },


    updateSectors(update, old){
        if(update.length == 0 && old.length == 0) return;
        for(var i in update){
            for(var k in old){

            }
        }

    },


    updateSectorDB(newIds, deleteIds){
        var payload = {payload: {newIds: newIds, deleteIds: deleteIds}};
        var url = "/api/user/sector/update";
        var callback = function (result) {
            $('.hint').html('已更新').show().fadeOut(2000);
        };
        Http.ajax(payload, url, callback);
    },


};

module.exports = UserUtil;

