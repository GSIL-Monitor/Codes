var EventEmitter = require('events').EventEmitter;
var assign = require('object-assign');

var AppDispatcher = require('../dispatcher/AppDispatcher');
var Const = require('../constant/Const');
var CHANGE_EVENT = 'change';
var FIR_CHANGE_EVENT = 'FIR_change';

var Functions = require('../util/Functions');

var store = {};
var old_store={};
var round;
var old_round;
var fir;
var old_fir = {};

var add_funding = {
    id: '',
    companyId: 0,
    round: 1010,
    roundDesc: '',
    investment: '',
    currency:'',
    precise:'',
    fundingDate:'',
    preMoney:'',
    postMoney:''
};

var add_fir = {
    id: '',
    fundingId: 0,
    investorId: 149,
    investment: '',
    currency:'',
    precise:''
};

var rel_investor = {
    id: '',
    name: ''
};


function get(id, data) {
    //data = Functions.transformFunding(data);
    store = data;
    updateOld(data);

    // round
    if (data.length > 0){
        changeRound(data[0].funding.id)
    }

    add_funding.companyId = id;

}

function getRound(id){
    for (var i in store){
        if(store[i].funding.id == id){
            round = store[i];
        }
    }
}


function change(id, name, value) {
    getRound(id);

    for(var k in round.funding){
        if (k == name)
            round.funding[k] = value.trim();
    }
}

function changeRound(id){
    for(var i in store){
       if(store[i].funding.id == id){
           round = store[i];
           old_round = old_store[i];
       }
    }

    add_fir.fundingId = id;
}


function updateOld(data) {
    old_store = Functions.clone(data);
}

function updateRoundFunding(data){
    for(var i in old_store){
        var update = {};
        if (old_store[i].funding.id == data.id){

            old_store[i].funding = Functions.clone(data)
        }
    }
}


function resetRoundFunding(){
    for(var i in store){
        var old_funding = {};
        if( store[i].funding.id == round.funding.id){

            old_funding = Functions.clone(old_store[i].funding)
            store[i].funding = old_funding;

            round.funding = old_funding;
        }
    }
}




/******* add ********/

function changeAddFunding(name, value) {
    add_funding[name] = value.trim();
}

function addFunding(data){
    var add_round ={};
    add_round.funding = data;
    add_round.fundingInvestorList = [];
    store.push(add_round);

    var old_arr = [];
    var old_round = Functions.clone(add_round);
    old_arr.push(old_round);
    old_store = old_arr.concat(old_store);

    round = add_round;
}



/****** delete ******/

function deleteFunding(){
    var update_store = [];
    for(var i in store){
        if(store[i].funding.id != round.funding.id){
            update_store.push(store[i]);
        }
    }
    store = update_store;
    old_store = Functions.clone(store);


    if(store.length > 0){
        round = store[0];
        old_round = Functions.clone(round);
    }
}



/**************** Funding investor rel **********************/
function changeInvestor(id){
    var list = round.fundingInvestorList;
    for(var i in list){
        if(list[i].fundingInvestorRel.id == id){
            fir = list[i].fundingInvestorRel;
            old_fir = Functions.clone(fir);
        }
    }
}

function changeAddFIR(name, value){
    add_fir[name] = value.trim();
}

function changeFIR(name, value){
    fir[name] = value.trim();
}

function addFIR(data){
    round.fundingInvestorList.push(data);
}

function deleteFIR(){
    var update_fiList = [];
    var fiList = round.fundingInvestorList;
    for(var i in fiList){
        if(fiList[i].fundingInvestorRel.id != fir.id){
            update_fiList.push(fiList[i]);
        }
    }

    round.fundingInvestorList = update_fiList;
}



const FundingStore = assign({}, EventEmitter.prototype, {
    get(){
        return store;
    },

    getOld(){
        return old_store;
    },

    getRound(){
        return round;
    },

    getOldRound(){
        return old_round;
    },

    getAdd(){
        return add_funding;
    },

    emitChange: function() {
        this.emit(CHANGE_EVENT);
    },

    addChangeListener: function(callback) {
        this.on(CHANGE_EVENT, callback);
    },

    removeChangeListener: function(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    },


    /************* Funding Investor Rel *************/
    getFIR(){
        return fir;
    },

    getOldFIR(){
        return old_fir;
    },

    getAddFIR(){
        return add_fir;
    },

    emitFIRChange: function() {
        this.emit(FIR_CHANGE_EVENT);
    },

    addFIRChangeListener: function(callback) {
        this.on(FIR_CHANGE_EVENT, callback);
    },

    removeFIRChangeListener: function(callback) {
        this.removeListener(FIR_CHANGE_EVENT, callback);
    }


});

AppDispatcher.register(function (action) {

    //console.log(action);
    switch (action.actionType) {


        case Const.GET_FUNDING:
            get(action.id, action.data);
            FundingStore.emitChange();
            break;

        case Const.CHANGE_FUNDING:
            change(action.id, action.name, action.value);
            FundingStore.emitChange();
            break;

        case Const.CHANGE_ROUND:
            changeRound(action.id);
            FundingStore.emitChange();
            break;

        case Const.UPDATE_FUNDING:
            updateRoundFunding(action.data);
            FundingStore.emitChange();
            break;

        case Const.RESET_FUNDING:
            resetRoundFunding();
            FundingStore.emitChange();
            break;

        case Const.CHANGE_ADD_FUNDING:
            changeAddFunding(action.name, action.value);
            FundingStore.emitChange();
            break;

        case Const.ADD_FUNDING:
            addFunding(action.data);
            FundingStore.emitChange();
            break;

        case Const.DELETE_FUNDING:
            deleteFunding();
            FundingStore.emitChange();
            break;

        // Funding investor rel
        case Const.CHANGE_INVESTOR:
            changeInvestor(action.id);
            FundingStore.emitFIRChange();
            break;

        case Const.CHANGE_FIR:
            changeFIR(action.name, action.value);
            FundingStore.emitFIRChange();
            break;

        case Const.CHANGE_ADD_FIR:
            changeAddFIR(action.name, action.value);
            FundingStore.emitFIRChange();
            break;

        case Const.ADD_FIR:
            addFIR(action.data);
            FundingStore.emitChange();
            break;

        case Const.DELETE_FIR:
            deleteFIR();
            FundingStore.emitChange();
            break;


        default:
            break;
    }
});


module.exports = FundingStore;
