var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');
var OrgSelectList = require('./OrgSelectList.react');
var Functions =require('../../../../../../react-kit/util/Functions');
const AddOrgList = React.createClass({

    render(){
        var data = this.props.data;
        return (
            <div className="create-company-form">

                <div className='cc-form-left cc-org-left'>
                    <span>机构列表</span>
                </div>

                <div className="cc-form-right">
                    <OrgSelectList data={data}/>
                </div>
            </div>
        )

    }
});
module.exports = AddOrgList;


