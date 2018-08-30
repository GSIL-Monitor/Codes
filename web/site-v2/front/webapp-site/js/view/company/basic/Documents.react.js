var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../store/CompanyStore');
var CompanyActions = require('../../../action/CompanyActions');
var Functions = require('../../../../../react-kit/util/Functions');

const Documents = React.createClass({
    render(){
        var id = 0;
        if(this.props.data.length == 0)
            return null;

        var data = this.props.data;

        return(
            <section className="section-body section-document">
                <div className="section-round">
                    <div className="section-name name4">
                        相关<br/>文件
                    </div>
                </div>
                <div className="section-content file-list">
                    {data.map(function (result, index) {
                        return <DocumentItem key={index} data={result}/>;
                    })}

                </div>
            </section>
        )
    }

});

const DocumentItem = React.createClass({
    render(){
        var data = this.props.data;
        var link = '/file/'+data.link+'/'+data.name;
        return(
           <div className="file">
               <a href={link} target="_blank">{data.name}</a>
           </div>
        )
    }
});






module.exports = Documents;