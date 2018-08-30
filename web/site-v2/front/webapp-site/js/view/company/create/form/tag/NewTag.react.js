var React = require('react');
var Reflux = require('reflux');
var TagContent = require('../../../modal/tag/TagContent.react');
const NewTag = React.createClass({



    render(){
        return(
            <div className="create-company-form">
            <div className='cc-form-left'>
                <span>标签</span>
            </div>

            <div className="cc-form-right">
                <div className="form-input cc-invalid-center">
                    <TagContent from="createCompany"/>
                </div>

            </div>
        </div>
        )}

});


module.exports = NewTag;