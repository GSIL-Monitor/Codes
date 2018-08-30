var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ColdcallActions = require('../../action/ColdcallActions');

const ColdcallCompanies = React.createClass({

    render(){
        var data = this.props.data;
        if( data.companies == null ){
            return <div className='cc-match-hint'>觉得项目不错？请和公司匹配以添加项目</div>;
        }

        return(
            <div>
                <div className='cc-match-hint'>觉得项目不错？请和公司匹配以添加项目</div>
                <div>
                    { data.companies.map(function (result, index) {
                        return <ListElement key={index} data={result}/>;
                    }.bind(this))}
                </div>
            </div>
        )
    }

});

const ListElement = React.createClass({
    render(){
        var data = this.props.data;
        //console.log(data);
        return(
            <div className="match-item">
                <a className="m-r-10" onClick={this.clickRemove}>
                    <i className="fa fa-times remove-match"></i>
                </a>
                <a href={"/#/company/" + data.code + "/overview"} _blank>{data.name} (已匹配)</a>
            </div>
        )
    },

    clickRemove() {
        var code = this.props.data.code;
        ColdcallActions.remove(code);
    }
});

module.exports = ColdcallCompanies;

