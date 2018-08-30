var React = require('react');
var DropzoneComponent = require('react-dropzone-component');

var UploadFile = React.createClass({

    render(){
        //this.props.types
        var componentConfig = {
            iconFiletypes: [],
            showFiletypeIcon: true,
            postUrl: '/api/company/file/upload'
        };


        var djsConfig = {dictDefaultMessage: "点击选择文件 / 将文件拖入框内"};

        var eventHandlers = {success: this.successUpload};


        return(
            <DropzoneComponent  className="drop-zone"
                                config={componentConfig}
                                eventHandlers={eventHandlers}
                                djsConfig={djsConfig}/>
        )
    },

    successUpload: function (result) {
        eval("var json=" + result.xhr.response);
        var file = {
            fileName: json.fileName,
            gridId: json.gridId
        };

        this.props.success(file);

        //CreateCompanyActions.addUploadedFile(file);
    }


})

module.exports = UploadFile;


//var eventHandlers = {
//    // This one receives the dropzone object as the first parameter
//    // and can be used to additional work with the dropzone.js
//    // object
//    init: null,
//    // All of these receive the event as first parameter:
//    drop: null,
//    dragstart: null,
//    dragend: null,
//    dragenter: null,
//    dragover: null,
//    dragleave: null,
//    // All of these receive the file as first parameter:
//    addedfile: null,
//    removedfile: null,
//    thumbnail: null,
//    error: null,
//    processing: null,
//    uploadprogress: null,
//    sending: null,
//    success: this.successUpload,
//    complete: null,
//    canceled: null,
//    maxfilesreached: null,
//    maxfilesexceeded: null,
//    // All of these receive a list of files as first parameter
//    // and are only called if the uploadMultiple option
//    // in djsConfig is true:
//    processingmultiple: null,
//    sendingmultiple: null,
//    successmultiple: null,
//    completemultiple: null,
//    canceledmultiple: null,
//    // Special Events
//    totaluploadprogress: null,
//    reset: null,
//    queuecompleted: null
//};