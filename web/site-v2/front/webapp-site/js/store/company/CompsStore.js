var Reflux = require('reflux');
var $ = require('jquery');
var CompsActions = require('../../action/company/CompsActions');
var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');

const CompsStore = Reflux.createStore({
    store: {
        update: false,
        showAll: false,
        companyId: null,
        list: [],
        updateList: [],
        newList: [],
        deleteList: []
    },

    init(){
        this.listenToMany(CompsActions);
    },

    onGet(id){
        //if(this.store.companyId == id) return;
        this.store.companyId = id;
        var payload = {payload: {id: id}};
        var url = "/api/company/comps/list";
        var callback = function (result) {
            //console.log(result);
            if (result.code == 0) {
                this.store.list = result.comps;
                this.store.updateList = Functions.clone(result.comps);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onShowAll(){
        if(this.store.showAll)
            this.store.showAll = false;
        else
            this.store.showAll = true;
        this.trigger(this.store);
    },

    onUpdate(){
        if(this.store.update)
            this.store.update = false;
        else
            this.store.update = true;
        this.trigger(this.store);
    },

    onSubmit(){
        var newList = this.store.newList;
        var addIds = [];
        if(newList.length> 0){
            for(var i in newList){
                addIds.push(newList[i].id);
            }
        }


        var payload = {payload: {
                        deleteIds: this.store.deleteList,
                        addIds: addIds,
                        companyId: this.store.companyId
                        }};
        var url = "/api/company/comps/update";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.list = this.store.updateList.concat(this.store.newList);
                this.store.updateList = Functions.clone(this.store.list);
                this.store.newList = [];
                this.store.deleteList = [];
                this.store.update = false;
                $('.hint').html('已更新').show().fadeOut(3000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);

        document.body.style.overflow = 'auto';
    },

    onDelete(id){
        var list = this.store.updateList;
        for(var i in list){
            if(id == list[i].id){
                list.splice(i, 1);
                this.store.deleteList.push(id);
            }
        }
        this.trigger(this.store);
    },

    onDeleteNew(id){
        var list = this.store.newList;
        for(var i in list){
            if(id == i){
                list.splice(i,1);
            }
        }

        this.trigger(this.store);
    },

    onAddNew(list){
        //this.store.newList = list;
        //console.log(this.store);
        //this.trigger(this.store);
        //$('#add-comps-modal').hide();
    }


});


module.exports = CompsStore;