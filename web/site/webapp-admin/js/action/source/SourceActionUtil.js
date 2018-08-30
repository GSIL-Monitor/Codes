
var SourceActionUtil = {

    sourceFilter(source, filter){

        var result = [];
        source.forEach(function(e){
            var element = {};
            var detail = [];
            for(var k in filter){
                var value = e[k];
                var show = null;
                //if(value != null && value !=""){
                    show = filter[k]+':  '+ value;
                    detail.push(show);
                //}
            }
            element.head = SourceActionUtil.getSourceInfo(e.source, e.sourceId);
            element.detail = detail;

            result.push(element);
        });
        return result;
    },

    getSourceInfo: function(source, id){
        var sourceName;
        var sourceUrl;
        var sourceMemberUrl = '';
        var sourceInvestorUrl = '';

        switch (source){
            case 13010:
                sourceName = 'JD';
                sourceUrl = '';
                break;
            case 13020:
                sourceName = '36Kr';
                sourceUrl = 'https://rong.36kr.com/home/'+id+'/overview';
                sourceMemberUrl = 'https://rong.36kr.com/userinfo/' + id;
                sourceInvestorUrl = 'https://rong.36kr.com/organization/' + id;
                break;
            case 13030:
                sourceName = 'IT桔子';
                sourceUrl = 'https://itjuzi.com/home/'+id;
                sourceMemberUrl = 'https://itjuzi.com/person/'+id;
                sourceInvestorUrl = 'https://itjuzi.com/investfirm/' + id;
                break;
            case 13040:
                sourceName = '创业谱';
                sourceUrl = '';
                break;
            case 13050:
                sourceName = '拉勾';
                sourceUrl = 'http://www.lagou.com/gongsi/'+id+'.html';
                //sourceMemberUrl = sourceUrl;
                break;
            case 13051:
                sourceName = '内推';
                sourceUrl = 'http://www.neitui.me/home/detail/domain='+id+'.html';
                sourceMemberUrl = sourceUrl;
                break;
            case 13052:
                sourceName = '周伯通';
                sourceUrl = 'http://www.jobtong.com/e/'+id;
                sourceMemberUrl = sourceUrl;
                break;
            case 13053:
                sourceName = '智联';
                sourceUrl = '';
                break;
            case 13054:
                sourceName = '前程无忧';
                sourceUrl = '';
                break;
            case 13060:
                sourceName = '点名时间';
                sourceUrl = '';
                break;
            case 13070:
                sourceName = '创业邦';
                sourceUrl = '';
                break;
            case 13080:
                sourceName = '百度';
                sourceUrl = '';
                break;
            case 13081:
                sourceName = '好搜';
                sourceUrl = '';
                break;

        }

        var sourceHead = {};
        sourceHead.sourceName = sourceName;
        sourceHead.sourceUrl = sourceUrl;
        sourceHead.sourceMemberUrl = sourceMemberUrl;
        sourceHead.sourceInvestorUrl = sourceInvestorUrl;

        return sourceHead;
    }

};



module.exports = SourceActionUtil;



