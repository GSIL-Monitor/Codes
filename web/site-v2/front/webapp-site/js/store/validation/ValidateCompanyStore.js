var Reflux = require('reflux');
var $ = require('jquery');
var ValidateCompanyActions = require('../../action/validation/ValidateCompanyActions');
var Functions = require('../../../../react-kit/util/Functions');
var ValidateUtil = require('../../util/ValidateUtil');
var Http = require('../../../../react-kit/util/Http');


const ValidateCompanyStore = Reflux.createStore({
    store: {
        validateDate: false,
        validateLocation: false
    },

    init(){
        this.listenToMany(ValidateCompanyActions);
    },

    onValidateDate(value){
        if(!ValidateUtil.validateDate(value)){
            this.store.validateDate = true;
        }else{
            this.store.validateDate = false;
        }
        this.trigger(this.store);
    },


    onSubmit(CompanyActions){
        var store = this.store;
        for(var i in store){
            if(store[i]) return;
        }
        CompanyActions.comfirm();
        //return 'false';
    }

})



module.exports = ValidateCompanyStore;