var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Modal = require('../../modal/Modal.react');

var UserInfoModel = React.createClass({

    render(){
        return  <Modal id="userInfo"
                       name="修改用户信息"
                       type="userInfo"
            />
    }

});


module.exports = UserInfoModel;