var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ColdcallActions = require('../../action/ColdcallActions');
var Functions =require('../../../../react-kit/util/Functions');

const ColdcallDetail = React.createClass({

    render(){
        var data = this.props.data;
        var cc = data.coldcall;
        if( cc == null ){
            return <div className="all-block"></div>;
        }
        var type = "邮件";
        var link = "";
        if(cc.coldcallType==24020){
            type = "微信";
            link = (<div><a href={cc.url} target="_blank">点击查看原文</a></div>)
        }
        else if(cc.coldcallType==24030){
            type = "在线";
            link = (<div>网站: <a href={cc.url} target="_blank">{cc.url}</a></div>)
        }

        var content = cc.content;

        Functions.updateTitle('coldcall',cc.name);
        return(
            <div className="cc-detail">
                <div className="cc-basic">
                    <div className="cc-title">{cc.name}</div>
                    <div className="cc-from">{type}</div>
                    <div className="cc-date">{(new Date(cc.createTime)).format("yyyy-MM-dd hh:mm:ss")}</div>
                </div>
                <div className="cc-file">
                    { data.files.map(function (result, index) {
                        //console.log(result);
                        return <ListElement key={index} data={result}/>;
                    }.bind(this))}
                </div>


                <div className="cc-content">
                    <pre>
                        {content}
                    </pre>
                </div>
                {link}

            </div>
        )
    }

});

const ListElement = React.createClass({
    render(){
        var data = this.props.data;
        return(
            <div className="file-item">
                <a className="a-cc-file" href={"/file/"+data.link+"/"+data.filename} target="_blank">
                    {data.filename}
                </a>
            </div>
        )
    }
});

module.exports = ColdcallDetail;

