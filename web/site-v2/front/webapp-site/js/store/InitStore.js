var Reflux = require('reflux');
var $ = require('jquery');
var InitActions = require('../action/InitActions');

const InitStore = Reflux.createStore({
    store:{
        code: null,
        demodayId: null,
        scoreType: null,
        companyName: null
    },

    init(){
        this.listenToMany(InitActions);
    },

    onInitCompany(code){
        this.store.code = code;
        this.trigger(this.store);
    },

    onInitDemoDayScore(id, code, type){
        this.store.demodayId = id;
        this.store.code = code;
        this.store.scoreType = type;
        this.trigger(this.store);
    },

    onInitCompleteCompany(id, code){
        this.store.demodayId = id;
        this.store.code = code;
        this.trigger(this.store);
    }
});

module.exports = InitStore;