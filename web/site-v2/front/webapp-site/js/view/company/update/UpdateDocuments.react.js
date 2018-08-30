var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var UploadFile = require('../create/UploadFile.react');

const UpdateFiles = React.createClass({

    render(){
        var data = this.props.data;
        var documents = data.updateDocuments;
        var news = data.newDocuments;

        var types = ['.pdf', '.ppt', '.doc', '.docx'];

        var updateClass = "section-round ";
        if(data.from == 'demodayAdd'){
            if(documents.length == 0 && news.length == 0)
                updateClass += 'section-must-update'
        }

        return(
            <section className="section-body end-section">
                <div className={updateClass}>
                    <div className="section-name name4">
                        相关<br/>文件
                    </div>
                </div>
                <div className="section-content">
                    <Documents data={documents} />
                    <AddDocuments data={news} />
                    <UploadFile className="upload-zone"
                                types={types}
                                success={this.success}/>
                </div>
            </section>
        )
    },

    success(file){
        CompanyActions.addUploadedFile(file);
    }

});


const Documents = React.createClass({
    render(){
        var data = this.props.data;
        if(data.length == 0) return null;

        return(
            <div className="update-file-list">
                {data.map(function (result, index) {
                    return <DocumentItem key={index} data={result}/>;
                })}
            </div>
        )
    }
});



const DocumentItem = React.createClass({
    render(){
        var data = this.props.data;
        var link = '/file/'+data.link;
        var className="label label-file "+this.props.className;

        return(
            <div className={className}>
                {data.name}
                <i className="fa fa-times m-l-10 label-close right" onClick={this.delete}></i>
            </div>
        )
    },

    delete(e){
        CompanyActions.deleteDocument(this.props.data.id);
    }
});


const AddDocuments = React.createClass({
    render(){
        var data = this.props.data;
        if(data.length == 0) return null;

        return(
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
        var link = '/file/'+data.link;
        var className="label label-file "+this.props.className;

        return(
            <div className={className}>
                {data.name}
                <i className="fa fa-times m-l-10 label-close right" onClick={this.delete}></i>
            </div>
        )
    },

    delete(e){
        CompanyActions.deleteNewDocument(this.props.id);
    }
});


module.exports = UpdateFiles;