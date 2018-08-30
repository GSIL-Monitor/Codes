
var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var Functions = require('../../../../../react-kit/util/Functions');

const RoleTypeItem = React.createClass({


    render(){
        var role = this.props.data;
        var list = this.props.roleList;
        var flag;
        if (list.length > 0) {
            for (var i in list) {
                if (role.value == list[i].value) {
                    if (list[i].selected)
                        flag = true;
                }
            }
        }
        var className = 'product-select user-role-r';
        if (flag) className += ' product-selected ';
        var cellClass='new-org-item admin-user-role m-l-10 ';
        if(this.props.modal&&role.value==25080){
            cellClass+='m-l-72'
        }
        return (
            <div className={cellClass}>
                <div >
                    <div className={className} onClick={this.click}></div>
                    <span>{role.name}</span>
                </div>

            </div>
        )
    },

    click(){
        this.props.onClick(this.props.data.value);
    }
});
module.exports = RoleTypeItem;