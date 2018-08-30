var Reflux = require('reflux');
var $ = require('jquery');
var LocationActions = require('../action/SearchLocationActions');
var Http = require('../util/Http');
var SearchUtil = require('../util/SearchUtil');
var Functions = require('../util/Functions');

var CompanyStore  = require('../../webapp-site/js/store/CompanyStore');
var CreateCompanyStore = require('../../webapp-site/js/store/CreateCompanyStore');

var ValidateCompanyStore = require('../../webapp-site/js/store/validation/ValidateCompanyStore');
var NewCompanyStore = require('../../webapp-site/js/store/validation/NewCompanyStore');

var NewCollectionStore = require('../../webapp-site/js/store/collection/NewCollectionStore');

const SearchLocationStore = Reflux.createStore({
    store:{
        location: null,
        locationId: null,
        match: null,
        hint: null,
        selected: null,
        from: null,
        validateLocation: true
    },

    init() {
        this.listenToMany(LocationActions);
    },

    onInit(value, id, from){
        this.store.location = value;
        this.store.locationId =  id;
        this.store.from = from;
        this.trigger(this.store);
    },

    onGet(value){
        if(Functions.isNull(value))
            return;

        var params = {data: value, field: 'location'};
        var url = '/api/search/complete';
        var callback =  function(result) {
            this.store.hint = result;
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(params, url, callback);
    },

    onChange(value){
        this.store.selected = null;
        this.store.location = value;
        this.onGet(value);
        this.trigger(this.store);
    },

    onSelect(value){
        this.store.selected = value;
        this.trigger(this.store);
    },

    onUnselect(){
        this.store.selected = null;
        this.trigger(this.store);
    },

    onKeydown(value){
        var result;

        if(value === 13){
            this.onClickSearch(this.store.location)
        }

        if(value ===38 || value === 40){
            result = SearchUtil.getLocationSelected(value, this.store.selected, this.store.hint);
            this.store.selected = result;
            this.trigger(this.store);
        }

    },

    onClickSearch(value){
        if (this.store.from == 'newCollection') {
            if (this.store.selected == null)
                this.getLocation(value);
            else
                NewCollectionStore.addNewLocation(this.store.selected);
            return;
        }


        var result = SearchUtil.doLocationMatch(this.store);
        this.store = result.store;
        this.store.validateLocation = result.validate;
        if(this.store.from == 'updateCompany'){
            CompanyStore.store.updateCompany.location = this.store.location;
            CompanyStore.store.updateCompany.locationId = this.store.locationId;
            ValidateCompanyStore.store.validateLocation = this.store.validateLocation;
            CompanyStore.trigger(CompanyStore.store);
            ValidateCompanyStore.trigger(ValidateCompanyStore.store);
        }

        if(this.store.from =='createCompany'){
            CreateCompanyStore.store.company.locationId = this.store.locationId;
            CreateCompanyStore.store.location = this.store.location;
            CreateCompanyStore.trigger(CreateCompanyStore.store);
            NewCompanyStore.store['locationId'].show = false;
            NewCompanyStore.store['locationId'].validation = true;
            NewCompanyStore.trigger(NewCompanyStore.store);

        }

        this.trigger(this.store);
    },

    onValidateLocation(){
        //console.log(this.store.locationId)
        //if(this.store.from == 'updateCompany'){
        //    if(this.store.locationId >=0){
        //        CompanyStore.store.validateLocation = false;
        //    } else{
        //        CompanyStore.store.validateLocation = true;
        //    }
        //    CompanyStore.trigger(CompanyStore.store);
        //}
    },

    getLocation(value){
        var params = {payload:{name: value}};
        var url = '/api/company/location/getByName';
        var callback =  function(result) {
            var location = {};
            location.name = value;
            if(result.code == 0){
                if(result.id == null){
                    $('.hint').html('不存在该地点').show().fadeOut(3000);
                }
                else{
                    location.id = result.id;
                    NewCollectionStore.addNewLocation(location);
                }
            }else{
                $('.hint').html('不存在该地点').show().fadeOut(3000);
            }
        }.bind(this);

        Http.ajax(params, url, callback);
    }


});



module.exports = SearchLocationStore;