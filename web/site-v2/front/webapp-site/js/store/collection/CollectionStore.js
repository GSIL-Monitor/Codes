var Reflux = require('reflux');
var $ = require('jquery');
var CollectionActions = require('../../action/collection/CollectionActions');

var Functions = require('../../../../react-kit/util/Functions');
var Http = require('../../../../react-kit/util/Http');
var CollectionUtil = require('../../util/CollectionUtil');

const CollectionStore = Reflux.createStore({
    store: {
        timeline: null,
        timelineTotal: 0,

        collectionId: null, //collectionId 对应的collection
        collection:null,
        customCols:[], //自定义集合
        sysCols:[], //精选集合
        hotCols:[], //热门集合

        selected: null,
        pageSize: 10,
        loading: false,

        tags: [],
        locations: Functions.locationUseful(),

        selectedTags: [],
        selectedLocations: [],
        selectedRounds: [],
        //selectedBackgrounds: [],
        //selectedInvestors: [],
        //selectedDates: []

        filterTags: [],
        filterLocations: [],
        filterRounds: []
    },

    init(){
        this.listenToMany(CollectionActions);
    },

    onInit(){
        this.store.timeline = [{"id":60322,"code":"tuniuwang1204","name":"途牛网","brief":"平台大，待遇好，薪资高，面试一轮过","description":"途牛旅游网创立于2006年10月，以“让旅游更简单”为使命，为消费者提供由北京、上海、广州、深圳等180个城市出发的旅游产品预订服务，产品全面，价格透明，全年365天24小时400电话预订，并提供丰富的后续服务和保障。\n目前，途牛旅游网提供100万余种旅游产品供消费者选择，涵盖跟团、自助、自驾、邮轮、酒店、签证、景区门票以及公司旅游等，已成功服务累计超过1500万人次出游。\n同时基于途牛旅游网全球中文景点目录以及中文旅游社区，可以更好地帮助游客了解目的地信息，妥善制定好出游计划，并方便地预订旅程中的服务项目。","round":"0","establishDate":null,"location":"北京","tags":[{"confidence":null,"verify":null,"active":null,"createTime":1450854480000,"modifyTime":1450854480000,"createUser":null,"modifyUser":null,"id":107,"name":"旅游","type":11010,"weight":null,"novelty":1.6281},{"confidence":null,"verify":null,"active":null,"createTime":1450854589000,"modifyTime":1450854589000,"createUser":null,"modifyUser":null,"id":132,"name":"酒店","type":11010,"weight":null,"novelty":2.1493},{"confidence":null,"verify":null,"active":null,"createTime":1450854589000,"modifyTime":1450854589000,"createUser":null,"modifyUser":null,"id":153,"name":"社区","type":11010,"weight":null,"novelty":1.8623},{"confidence":null,"verify":null,"active":null,"createTime":1450854595000,"modifyTime":1450854595000,"createUser":null,"modifyUser":null,"id":447,"name":"目的地","type":11010,"weight":null,"novelty":3.1469},{"confidence":null,"verify":null,"active":null,"createTime":1450856829000,"modifyTime":1450856829000,"createUser":null,"modifyUser":null,"id":663,"name":"邮轮","type":11010,"weight":null,"novelty":3.5369},{"confidence":null,"verify":null,"active":null,"createTime":1450856848000,"modifyTime":1450856848000,"createUser":null,"modifyUser":null,"id":1155,"name":"自助游","type":11010,"weight":null,"novelty":2.7061},{"confidence":null,"verify":null,"active":null,"createTime":1450856857000,"modifyTime":1450856857000,"createUser":null,"modifyUser":null,"id":1355,"name":"景区","type":11010,"weight":null,"novelty":3.1084},{"confidence":null,"verify":null,"active":null,"createTime":1450856859000,"modifyTime":1450856859000,"createUser":null,"modifyUser":null,"id":1408,"name":"景点","type":11010,"weight":null,"novelty":3.624},{"confidence":null,"verify":null,"active":null,"createTime":1450857187000,"modifyTime":1450857187000,"createUser":null,"modifyUser":null,"id":2606,"name":"旅游网","type":11010,"weight":null,"novelty":3.925},{"confidence":null,"verify":null,"active":null,"createTime":1450857377000,"modifyTime":1450857377000,"createUser":null,"modifyUser":null,"id":4232,"name":"游客","type":11010,"weight":null,"novelty":3.2665},{"confidence":null,"verify":null,"active":null,"createTime":1456823135000,"modifyTime":1456823135000,"createUser":null,"modifyUser":null,"id":36801,"name":"门票","type":11010,"weight":null,"novelty":3.624},{"confidence":null,"verify":null,"active":null,"createTime":1459234890000,"modifyTime":1459234890000,"createUser":null,"modifyUser":null,"id":87264,"name":"旅程","type":11010,"weight":null,"novelty":3.6488}],"sectors":[{"confidence":1.0,"verify":"Y","active":"Y","createTime":1453874393000,"modifyTime":null,"createUser":null,"modifyUser":null,"id":10,"sectorName":"旅游户外","level":1,"parentId":null}]},{"id":2761,"code":"lvmama","name":"驴妈妈旅游网","brief":"","description":"驴妈妈旅游网是一个B2C在线旅游服务网站，提供自助游资讯及预订服务，隶属于上海景域文化传播有限公司。","round":"1130","establishDate":"2008-01-01","location":"上海","tags":[{"confidence":null,"verify":null,"active":null,"createTime":1450854480000,"modifyTime":1450854480000,"createUser":null,"modifyUser":null,"id":107,"name":"旅游","type":11010,"weight":null,"novelty":1.6281},{"confidence":null,"verify":null,"active":null,"createTime":1450854590000,"modifyTime":1450854590000,"createUser":null,"modifyUser":null,"id":178,"name":"B2C","type":11010,"weight":null,"novelty":1.5901},{"confidence":null,"verify":null,"active":null,"createTime":1450854594000,"modifyTime":1450854594000,"createUser":null,"modifyUser":null,"id":409,"name":"旅游综合服务","type":11010,"weight":null,"novelty":2.4677},{"confidence":null,"verify":null,"active":null,"createTime":1450854595000,"modifyTime":1450854595000,"createUser":null,"modifyUser":null,"id":429,"name":"目的地旅游","type":11010,"weight":null,"novelty":2.7149},{"confidence":null,"verify":null,"active":null,"createTime":1450854595000,"modifyTime":1450854595000,"createUser":null,"modifyUser":null,"id":430,"name":"国内长途游","type":11010,"weight":null,"novelty":3.155},{"confidence":null,"verify":null,"active":null,"createTime":1450856829000,"modifyTime":1450856829000,"createUser":null,"modifyUser":null,"id":662,"name":"出境游","type":11010,"weight":null,"novelty":2.4577},{"confidence":null,"verify":null,"active":null,"createTime":1450856832000,"modifyTime":1450856832000,"createUser":null,"modifyUser":null,"id":723,"name":"高端旅游","type":11010,"weight":null,"novelty":3.1011},{"confidence":null,"verify":null,"active":null,"createTime":1460138718000,"modifyTime":1460138718000,"createUser":null,"modifyUser":null,"id":127994,"name":"攻略与资讯","type":11010,"weight":null,"novelty":4.1803}],"sectors":[{"confidence":1.0,"verify":"Y","active":"Y","createTime":1453874393000,"modifyTime":null,"createUser":null,"modifyUser":null,"id":10,"sectorName":"旅游户外","level":1,"parentId":null}]}];
        this.trigger(this.store);
    },

    //onInit(){
    //    this.clean();
    //    this.getAllCollection();
    //    this.countComps();
    //    this.onListMore();
    //    this.trigger(this.store);
    //},

    onGetCollection(collectionId){
        this.clean();
        this.getAllCollection();
        this.store.collectionId = collectionId;
        this.countComps(collectionId);
        this.onListMore(collectionId);
        this.trigger(this.store);
    },

    clean(){
        this.store.timeline = null;
        this.store.timelineTotal = 0;
        this.store.loading = false;
        this.trigger(this.store);
    },

    countComps(collectionId){
        var payload = {payload: {collectionId:collectionId}};
        var url = "/api/company/collection/count/";
        if(collectionId){
             url +="collcomp";
        }else{
            url +="timeLine";
        }
        var callback = function (result) {
            if (result.code == 0) {
                this.store.timelineTotal = result.total;
            }
            this.trigger(this.store);
        }.bind(this);
        Http.ajax(payload, url, callback);
    },

    getAllCollection(){
        var payload = {payload: {}};
        var url = "/api/company/collection/list";
        var callback = function (result) {
            if (result.code == 0) {
                this.store.customCols=result.customCols;
                this.store.sysCols =result.sysCols;
                this.store.hotCols = result.hotCols;
            }
            this.trigger(this.store);
        }.bind(this);
        Http.ajax(payload, url, callback);
    },

    onDealUserScore(score, code){
        var payload = {payload: {score: score, code: code, type: "22010"}};
        var url = "/api/company/deal/score/modify";
        var callback = function (result) {
            if (result.code == 0) {
                CollectionUtil.changeScore(score,code,this.store.timeline)
            }
            this.trigger(this.store);
        }.bind(this);
        Http.ajax(payload, url, callback);
    },

    onListMore(){
        if (CollectionUtil.isLoading(this.store)) return;
        this.store.loading = true;
        var params = CollectionUtil.getLoadParam(this.store);
        var payload = {
            payload: {
                pageSize: this.store.pageSize,
                start: params.start,
                collectionId:this.store.collectionId
            }
        };
        var url = params.url;
        var callback = function (result) {
            if (result.code == 0 && result.list != null) {
                this.store.loading = false;
                CollectionUtil.setResult(result, this.store);
            }
            this.trigger(this.store);
        }.bind(this);

        Http.ajax(payload, url, callback);
    },

    onFollow(id){
        var payload = {payload: {collectionId:id}};
        var url = "/api/company/collection/follow";
        var callback = function (result) {
            if (result.code == 0) {
                CollectionUtil.followCollection(id,this.store);
            }
            this.trigger(this.store);
        }.bind(this);
        Http.ajax(payload, url, callback);
    },

    onUnFollow(id){
        var payload = {payload: {collectionId:id}};
        var url = "/api/company/collection/unfollow";
        var callback = function (result) {
            if (result.code == 0) {
                CollectionUtil.unFollowCollection(id,this.store);
            }
            this.trigger(this.store);
        }.bind(this);
        Http.ajax(payload, url, callback);
    },

    onFilter(data, type){
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

    onComfirmFilter(){
        $('.modal').hide();
        this.store.filterTags = Functions.clone(this.store.selectedTags);
        this.store.filterLocations = Functions.clone(this.store.selectedLocations);
        this.store.filterRounds = Functions.clone(this.store.selectedRounds);
        this.trigger(this.store);
    }

});

module.exports = CollectionStore;