var Reflux = require('reflux');
var $ = require('jquery');
var HeaderActions = require('./../action/HeaderActions');

const HeaderStore = Reflux.createStore({
    store:{
        router: null,
        search: '',
        searching: false
    },

    init() {
        this.listenToMany(HeaderActions);
    },

    onInit(){
        $('.search-hint').hide();
        this.trigger(this.store);
    },

    onInitSearch(value){
        this.store.search = value;
        this.store.searching = true;
        this.onRouter('search');
        this.trigger(this.store);
    },

    onRouter(value){
        $('.modal').hide();
        this.store.router = value;
        this.trigger(this.store);
    },

    onClickMobileSearch(){
        this.store.searching = true;
        this.trigger(this.store);
    },

    onClickSearchClose(){
        this.store.searching = false;
        this.trigger(this.store);
    },

    onClickMobileHeader(){
        if(this.store.mobileListShow)
            this.store.mobileListShow = false;
        else
            this.store.mobileListShow = true;
        this.trigger(this.store);
    }
});

module.exports = HeaderStore;