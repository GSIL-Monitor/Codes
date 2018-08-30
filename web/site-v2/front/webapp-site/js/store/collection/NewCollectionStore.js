var Reflux = require('reflux');
var $ = require('jquery');
var NewCollectionActions = require('../../action/collection/NewCollectionActions');

var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');
var CollectionUtil = require('../../util/CollectionUtil');

const NewCollectionStore = Reflux.createStore({
    store: {
        tags: [],
        locations: [],

        selectedTags: [],
        selectedLocations: [],
        selectedRounds: [],
        selectedBackgrounds: [],
        selectedInvestors: [],
        selectedDates: [],

        name:null
    },

    init(){
        this.listenToMany(NewCollectionActions);
    },

    onInit(){
        this.store.locations = Functions.locationUseful();
        this.trigger(this.store)
    },

    onSelect(data, type){
        if(type == 'tag'){
            this.store.selectedTags = CollectionUtil.selected(data, this.store.selectedTags);
        }else if(type == 'location'){
            this.store.selectedLocations = CollectionUtil.selected(data, this.store.selectedLocations);
        }else if(type == 'round'){
            this.store.selectedRounds = CollectionUtil.selected(data, this.store.selectedRounds);
        }else if(type == 'background'){
            this.store.selectedBackgrounds = CollectionUtil.selected(data, this.store.selectedBackgrounds);
        }else if(type == 'investor'){
            this.store.selectedInvestors = CollectionUtil.selected(data, this.store.selectedInvestors);
        }else if(type == 'date'){
            this.store.selectedDates = CollectionUtil.selected(data, this.store.selectedDates);
        }

        this.trigger(this.store);
    },


    getHotSectors(){

    },

    getHotTags(){

    },

    getLocations(){

    },

    addNewTag(tag){
        if(tag.id == null) return;
        tag.value = tag.id;
        this.store.tags = CollectionUtil.listAddUnique(this.store.tags, tag);
        this.store.selectedTags = CollectionUtil.listAddUnique(this.store.selectedTags, tag);
        this.trigger(this.store);
    },

    addNewLocation(location){
        if(location.id == null) return;
        location.value = location.id;
        this.store.locations = CollectionUtil.listAddUnique(this.store.locations, location);
        this.store.selectedLocations = CollectionUtil.listAddUnique(this.store.selectedLocations, location);
        this.trigger(this.store);
    },

    onChangeName(value){
        this.store.name = value;
        this.trigger(this.store);
    },

    onAdd(){
        if(this.store.selectedTags.length == 0){
            $('#new-collection-warn > .warn-body > .warn-content').html('标签必须选择');
            $('#new-collection-warn').show();
            return;
        }
        if(this.store.name == null) {
            $('#new-collection-warn > .warn-body > .warn-content').html('集合名称必须填写');
            $('#new-collection-warn').show();
            return;
        }


    }

});

module.exports = NewCollectionStore;