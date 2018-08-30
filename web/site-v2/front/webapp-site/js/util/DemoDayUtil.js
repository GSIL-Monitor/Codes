const DemoDayUtil = {

    rating(store, score, type){
        switch (type){
            case 'preScore':
                store.ratingPreScore = score; break;
            case 'industry':
                store.ratingIndustry = score; break;
            case 'team':
                store.ratingTeam = score; break;
            case 'product':
                store.ratingProduct = score; break;
            case 'gain':
                store.ratingGain = score; break;
            case 'preMoney':
                store.ratingPreMoney = score; break;
        }

        if(this.submitScore){
            store.submitScore = true;
        }
        return store;
    },

    getScores(store){
        var scores = [];
        scores.push((store.ratingIndustry==null||store.ratingIndustry==0)?store.score[0]:store.ratingIndustry);
        scores.push((store.ratingTeam==null||store.ratingTeam==0)?store.score[1]:store.ratingTeam);
        scores.push((store.ratingProduct==null||store.ratingProduct==0)?store.score[2]:store.ratingProduct);
        scores.push((store.ratingGain==null||store.ratingGain==0)?store.score[3]:store.ratingGain);
        scores.push((store.ratingPreMoney==null||store.ratingPreMoney==0)?store.score[4]:store.ratingPreMoney);
        return scores;
    },

    submitScore(store){
        var data = store;
        if( data.score[0] > 0 &&
            data.score[1] > 0 &&
            data.score[2] > 0 &&
            data.score[3] > 0 &&
            data.score[4] > 0 && (
            data.ratingIndustry > 0 ||
            data.ratingTeam > 0 ||
            data.ratingProduct > 0 ||
            data.ratingGain > 0 ||
            data.ratingPreMoney > 0
            )){
            return true;
        }
        else if( data.ratingIndustry > 0 &&
            data.ratingTeam > 0 &&
            data.ratingProduct > 0 &&
            data.ratingGain > 0 &&
            data.ratingPreMoney > 0 ){
            return false;
        }
    },


    getDemodayStatus(status){
        switch (Number(status)){
            case 26000:
                return '项目提交中';
            case 26005:
                return '项目提交结束';
            case 26010:
                return '打分初筛选中';
            case 26020:
                return '初筛选结束';
            case 26024:
                return '通知团队中';
            case 26027:
                return '通知团队结束';
            case 26030:
                return '会议进行中';
            case 26040:
                return '已结束';
        }
    },

    sortScores(list){
        var ranks = [];
        var nonRanks = [];
        for(var i in list){
            if(list[i].rank == null){
                nonRanks.push(list[i])
            }else{
                ranks.push(list[i])
            }
        }

        ranks = ranks.sort(function(a, b){
            return a.rank > b.rank ? 1 : -1;
        });


        return ranks.concat(nonRanks);
    }


};

module.exports = DemoDayUtil;