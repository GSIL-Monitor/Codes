/**
 * Created by jesse on 16/2/3.
 */
var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CreateCompanyStore = require('../../../../../store/CreateCompanyStore');
var CreateCompanyActions = require('../../../../../action/CreateCompanyActions');
var Functions = require('../../../../../../../react-kit/util/Functions');
var UploadFile = require('../../UploadFile.react');
var ValidateStore = require('../../../../../store/validation/NewCompanyStore');
var ValidateActions = require('../../../../../action/validation/NewCompanyActions');


const UploadBP = React.createClass({

    render(){

        var required;
        if(this.props.demodayId){
            required=   <span className='left-required'>*</span>;
        }
        return (
            <div className="create-company-form">
                <div className='cc-form-left'>
                     {required}
                    <span>上传BP</span>
                </div>

                <div className="cc-form-right">
                    <div className="form-input cc-invalid-center">
                        <UpdateFiles data={this.props.data}  demodayId={this.props.demodayId}/>
                    </div>

                </div>
            </div>);
    }
});
module.exports = UploadBP;

const UpdateFiles = React.createClass({

    mixins: [Reflux.connect(ValidateStore, 'validate')],

    render(){
        var hint;
        if(!Functions.isEmptyObject(this.state)) {
            var validate = this.state.validate.files;
            if (!Functions.isEmptyObject(validate)) {
                if (!validate.validation) {
                    hint = <span className="text-red">{validate.hint}</span>;
                }
            }
        }
        var types = ['.pdf', '.ppt', '.doc', '.docx'];

        return (
        <div className="upload-bp" >
            <AddDocuments data={this.props.data} />
            <UploadFile className="upload-zone"
                        success={this.successUpload}/>
            <div className="form-hint">
                {hint}
            </div>
        </div>
        )
    },

    successUpload(file){
        CreateCompanyActions.addUploadedFile(file);
        ValidateActions.uploadBp(file.length);

    }

});

const AddDocuments = React.createClass({
    render(){
        var data = this.props.data;
        if (data.length == 0) return null;

        return (
            <div className="update-file-list">
                {data.map(function (result, index) {
                    return <AddDocumentItem key={index} id={index} data={result} className="add-item"/>;
                })}
            </div>
        )
    }
});


const AddDocumentItem = React.createClass({
    render(){
        var data = this.props.data;

        var className = "label label-file " + this.props.className;

        return (
            <div className={className}>
                {data.fileName}
                <i className="fa fa-times m-l-10 label-close right" onClick={this.delete}></i>
            </div>
        )
    },

    delete(e){
        CreateCompanyActions.deleteFile(this.props.id);
    }
});


