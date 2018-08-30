var Reflux = require('reflux');
var $ = require('jquery');
var UserCompanyActions = require('../action/UserCompanyActions');

var Functions = require('../../../react-kit/util/Functions');
var Http = require('../../../react-kit/util/Http');
var ScoreUtil = require('../util/ScoreUtil');
const UserCompanyStore = Reflux.createStore({
    store: {
        code: null,
        nextCode: null,
        assignee: false,
        deal: null,
        x: null,
        notes: null,
        noteText: "",
        score:null,
        scores:[],
        noteAll: false,
        update: false
    },

    init(){
        this.listenToMany(UserCompanyActions);
    },

    onInit(code){
        this.onGetScore(code);
        this.onGetNote(code);
        this.getColdcall(code);
    },

    onAddDeal(id){
        var payload = {payload: {companyId: id}};
        var url = "/api/company/deal/add";
        this.trigger(this.store);
    },

    onScore(score){
        var payload ={payload: {code: this.store.code,
                                score: score,
                                type: '22010'}};

        var url = "/api/company/deal/score/modify";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.score=score;
                if(!Functions.isNull(this.store.nextCode)){
                    $('.hint').html('已更新评分, 跳转下一个~').show().fadeOut(2000);
                    window.location.href = './#/company/'+this.store.nextCode+'/overview';
                }else if(Functions.isNull(this.store.nextCode) && this.store.assignee)
                    $('.hint').html('任务全部完成~').show().fadeOut(3000);
                else
                    $('.hint').html('已更新评分').show().fadeOut(2000);
            } else {
                $('.hint').html('操作失败').show().fadeOut(2000);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onChange(name, value) {
        this.store[name] = value;
        this.trigger(this.store);
    },

    onNote( note, noteId){
        var payload = {
            payload: {
                code: this.store.code,
                note: note,
                noteId: noteId
            }
        };
        var url = "/api/company/deal/note/modify";
        var callback = function (result) {
            if (result.code == 0) {
                if (noteId == null) {
                    $('.hint').html('已添加!').show().fadeOut(2000);
                    this.store.noteText = "";
                    this.trigger(this.store);
                }
                else {
                    $('.hint').html('已更新!').show().fadeOut(2000);
                }
                this.onGetNote(this.store.code);
            } else {
                //if (noteId == null) {
                //    $('.hint').html('新增失败!').show().fadeOut(2000);
                //}
                //else {
                //    $('.hint').html('修改失败!').show().fadeOut(2000);
                //}
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onDelete(noteId){
        var payload = {
            payload: {
                noteId: noteId,
            }
        };
        var url = "/api/company/deal/note/delete";
        var callback = function (result) {
            if (result.code == 0) {
                $('.hint').html('已删除!').show().fadeOut(2000);
                this.onGetNote(this.store.code);
            } else {
                //$('.hint').html('删除失败!').show().fadeOut(2000);
            }
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onUpdate(){
        if (this.store.update)
            this.store.update = false;
        else
            this.store.update = true;
        this.trigger(this.store);
    },

    /******  show all *********/
    onShowNoteAll(){
        if (this.store.noteAll)
            this.store.noteAll = false;
        else
            this.store.noteAll = true;
        this.trigger(this.store);
    },

    /****  get ****/
    onGetScore(code){
        this.store.code = code;
        var payload = {payload: {code: code}};
        var url = "/api/company/deal/score/get";
        var callback = function (result) {
            if (result.code == 0) {
                if(result.scores == null) {
                    this.store.scores = null;
                    this.store.score = null;
                }
                else{
                    this.store.score= ScoreUtil.getDealUserScore(result.scores);
                    this.store.scores= ScoreUtil.removeSelfScore(result.scores);
                    this.store.nextCode = result.nextCode;
                    this.store.assignee = result.assignee;
                }
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onGetNote(code){
        this.store.code = code;
        var payload = {payload: {code: code}};
        var url = "/api/company/deal/note/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.notes = result.notes;
            } else {
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    getColdcall(code){
        $('.user-cc-content').hide();
        $('.container').css('margin-left', 'auto');
        $('.header').css('z-index', '999');

        this.store.code = code;
        var payload = {payload: {code: code}};
        var url = "/api/company/coldcall/get";
        var callback = function (result) {
            if(result.code == 0) {
                this.store.coldcall = result.coldcall;
                this.store.files = result.files;
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    }


});


module.exports = UserCompanyStore;