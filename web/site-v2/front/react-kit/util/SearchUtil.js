var $ = require('jquery');
var Functions = require('./Functions');

const SearchUtil = {

    listAddUnique(list, item, type){
        var flag = false;
        if(list.length == 0){
            list.push(item);
        }
        else{
            for(var i in list){

                if(type == 'company'){
                    if(item == null) break;
                    if(list[i] == null) break;
                    if(item.name == list[i].name){
                        flag = true;
                    }
                }
                else if (type == 'tag'){
                    if(item.id == list[i].id){
                        flag = true;
                    }
                }

            }

            if(!flag) list.push(item);
        }

        return list;
    },

    selectUpOrDown(value, selected, list){
        var result;
        if(list.length == 0){
            return;
        }

        if(Functions.isNull(selected)){

            if(value === 40){
                result = list[0];
            }

            if(value === 38){
                result = list[list.length-1];
            }

        }else{
            for(var i=0; i<list.length; i++){
                if(list[i] == selected){

                    if(value === 40){
                        if(i == list.length-1)
                            result = list[0];
                        else
                            result = list[i+1];
                    }

                    if(value === 38){
                        if(i == 0)
                            result = list[list.length-1];
                        else
                            result = list[i-1]
                    }
                }
            }
        }

        return result;
    },


    getSelected(value, selected, hint){
        var list = [];
        var result = null;
        var companies;
        var keywords;
        for(var k in hint){
            if(k == 'name'){
                companies = hint[k];
            }else if( k =='keyword'){
                keywords = hint[k]
            }
        }

        if(companies != null && companies.length != 0){
            list = list.concat(companies);
        }

        if(keywords != null && keywords.length != 0){
            list = list.concat(keywords);
        }


        result = this.selectUpOrDown(value, selected, list);

        return result;

    },

    doSearch(type, search, selected){
        $('.search-hint').hide();
        var url;

        if(Functions.browserVersion() == 'mobile'){
            for(var k in selected){
                if(k == 'code'){
                    url="./#/company/"+selected[k]+"/overview";
                    return url;
                }
            }

            for(var k in selected){
                if(k == 'name'){
                    url ="./#/search/open/"+ selected[k];
                    return url;
                }
            }

            if(Functions.isNull(search))
                url = './#/search/open/';
            else
                url = "./#/search/open/"+search;
            return url;
        }

        //if(type != null){
        //    url= "/search/#/"+type+"/"+ search;
        //    return url
        //}

        for(var k in selected){
            if(k == 'code'){
                url="/#/company/"+selected[k]+"/overview";
                return url;
            }
        }

        for(var k in selected){
            if(k == 'name'){
                url ="/search/#/open/"+ selected[k];
                return url;
            }
        }


        url = "/search/#/open/"+ search;
        return url;

    },

    getCompanySelected(value, selected, hint){
        var list = hint.name;
        var result = this.selectUpOrDown(value, selected, list);
        return result;
    },

    getLocationSelected(value, selected, hint){
        var list = hint.location;
        var result = this.selectUpOrDown(value, selected, list);
        return result;
    },

    getInvestorSelected(value, selected, hint){
        var list = hint.investor;
        var result = null;

        result = this.selectUpOrDown(value, selected, list);
        return result;
    },

    getTagSelected(value, selected, hint){
        var list = hint.keyword;
        var result = this.selectUpOrDown(value, selected, list);
        return result;
    },

    doCompanyMatch(store){
        $('.search-company-hint').hide();
        store.matches = this.listAddUnique(store.matches, store.selected, 'company');
        store.value = null;

        return store;
    },

    doLocationMatch(store){
        $('.search-location-hint').hide();
        if(Functions.isNull(store.selected))
            return {store:store, validate: true };

        store.match = store.selected;
        store.location = store.match.name;
        store.locationId = store.match.id;

        return {store:store, validate: false };
    },

    doInvestorMatch(store){
        $('.search-investor-hint').hide();
        if(Functions.isNull(store.selected))
            return store;

        store.match = store.selected;
        store.value = store.match.name;
        store.id = store.match.id;

        return store;
    },

    doTagMatch(store, matches){
        $('.search-tag-hint').hide();

        if(Functions.isNull(store.selected)){
            return store;
        }

        var matches = this.listAddUnique(matches, store.selected, 'tag');

        return matches;
    }

};

module.exports = SearchUtil;