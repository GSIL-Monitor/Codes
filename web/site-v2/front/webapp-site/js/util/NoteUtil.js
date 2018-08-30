const NoteUtil = {
    parseTimestamp(time){

        return new Date(time).format("yyyy-MM-dd hh:mm:ss")
    },

    parseScoreColor(score){
        var className;
        switch (Number(score)){
            case 4:
                className='mark-4' ; break;
            case 3:
                className='mark-3' ; break;
            case 2:
                className='mark-2' ; break;
            case 1:
                className='mark-1' ; break;
        }
        return ' '+ className + ' mark-color ' ;
    }

}

module.exports = NoteUtil;