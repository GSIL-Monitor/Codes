/**
 * Created by haiming on 16/2/3.
 */
const ScoreUtil= {
    getDealUserScore(scores){
        var score;
        for (var k in scores) {
            if (scores[k].owner) {
                score = scores[k].score;
            }
        }
        return score;
    },

    removeSelfScore(scores){
        if(scores.length ==0) return [];
        var result = [];
        for(var i in scores){
            if(!scores[i].owner){
                result.push(scores[i]);
            }
        }
        return result;
    }
}
module.exports = ScoreUtil;