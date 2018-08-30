const SearchUtil ={

    getSearchInfo(store){
        var type = store.type;
        var url = "/api/search/";
        var params;

        url += "open";
        params = {data:{
            input: store.search,
            sort: store.sort,
            start:store.list.length,
            date: store.filterDates,
            round: store.filterRounds,
            location: store.filterLocations,
            sector_l1: store.filterSectors
        }};

        return {params:params, url:url};

    },

    isInList(value, list){
        if(list == null) return;
        if(list.length == 0) return;
        for(var i in list){
            if(list[i] == value) return true;
        }
        return false;
    },

    getSectorName(id, list){
        for(var i in list){
            if(list[i].id == id) return list[i].sectorName;
        }
    },

    getSelectedName(id, list){
        for(var i in list){
            if(list[i].value == id) return list[i].name;
        }
    },

    getDateName(id, list){
        for(var i in list){
            if(list[i] == id) return list[i];
        }
    },


    listChange(value, list){
        var flag = false;
        if(list.length == 0){
            list.push(value);
        }else{
            for(var i in list){
                if(list[i] == value){
                    list.splice(i, 1);
                    flag = true;
                }
            }

            if(!flag) list.push(value);
        }

        return list;
    },

    removeFromList(value, list){
        for(var i in list){
            if(list[i] == value)
                list.splice(i, 1);
        }
    }

};

module.exports = SearchUtil;



//switch (type) {
//    case 'open':
//
//        break;
//    //case 'company':
//    //    url += "company";
//    //    params = {data:{name: store.names,
//    //                    sort: store.sort,
//    //                    start:store.list.length,
//    //                    date: store.filterDates,
//    //                    round: store.filterRounds,
//    //                    location: store.filterLocations
//    //               }};
//    //    break;
//    //case 'keyword':
//    //    url += "keyword";
//    //    params = {data:{keyword: store.keywords,
//    //                    sort: store.sort,
//    //                    start:store.list.length,
//    //                    date: store.filterDates,
//    //                    round: store.filterRounds,
//    //                    location: store.filterLocations
//    //              }};
//    //    break;
//
//    //case 'latest':
//    //    url += "top";
//    //    params = {
//    //        sort: store.sort,
//    //        start:store.list.length,
//    //        date: store.filterDates,
//    //        round: store.filterRounds,
//    //        location: store.filterLocations,
//    //        sector_l1: store.filterSectors
//    //    };
//    //    break;
//
//    default :
//        break;
//
//}