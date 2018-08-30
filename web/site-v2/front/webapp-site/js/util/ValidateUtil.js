const ValidateUtil = {

    validateDate(date){
        var reg = new RegExp("^[0-9]{4}-[0-9]{2}-[0-9]{2}$");
        if(reg.test(date)) return true;
        return false;
    },

    validateMoney(value){
        var reg = new RegExp("^[0-9]{1}[0-9]*$");
        if(reg.test(value)) return true;
        return false;
    },

    validateURL(link){
        var expression = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
        var reg = new RegExp(expression);
        if(reg.test(link)) return true;
        return false;
    },

    /**true是正确的时间日期  code是错误码**/
    checkDate(date){
        var code = 0;//code代表一些列错误码
        var reg = new RegExp("^[0-9]{4}-[0-9]{2}-[0-9]{2}$");
        //不满足 yyyy-mm-dd格式直接返回错误
        if (!reg.test(date)) {
            code = 1;//格式不正确
            return code;
        }

        var year = date.substring(0, 4);
        var month = date.substring(5, 7);
        var day = date.substring(8, 10);
        var leanYear = false;
        //检查年份
        if (year < 0 || year > 9999) {
            code = 2;//年份不正确
            return code;
        }
        else {
            // leanYear true则是闰年
            leanYear = (year % 4 == 0 && year % 100 != 0 || year % 400 == 0);
        }
        //年满足条件，检查月份
        if (month < 0 || month > 12) {
            code = 3;//月份不正确
            return code;
        }

        else {
            switch (month) {
                case '01':
                case '03':
                case '05':
                case '07':
                case '08':
                case '10':
                case '12':
                    if (day < 0 || day > 31) {
                        code = 4;//日期不正确
                        return code;
                    }
                    break;

                case '02':
                    if (leanYear) {
                        if (day < 0 || day > 29) {
                            code = 4;
                            return code;
                        }
                    }
                    else {
                        if (day < 0 || day > 28) {
                            code = 4;
                            return code;
                        }
                    }
                    break;
                case '04':
                case '06':
                case '09':
                case '11':
                    if (day < 0 || day > 30) {
                        code = 4;
                        return code;
                    }
                    break;
                default :
                    break;
            }

        }
        return code;
    },
    /**
     * check phone number
     * */
    checkNumber(value){
        var re = /\d*/;
        var result;
        if (value != null) {
            result = value.match(re);
            return (result == value);
        }
        else {
            return true;
        }
    },
    /**检测输入的金额*/
    validateMoney(value){
        var reg = /^[1-9]{1}[0-9]*$/;
        if (value!=''&&value.length >= 1) {
            return reg.test(value);
        }
        else{
            return true;
        }
    },
    validateShares(value){
        var req = /^([1-9]\d*|0)(\.(\d)*)?$/;
        if (value!='' && value.length >= 1) {
            return req.test(value)
        }
        else {
            return true;
        }

    },

};

module.exports = ValidateUtil;