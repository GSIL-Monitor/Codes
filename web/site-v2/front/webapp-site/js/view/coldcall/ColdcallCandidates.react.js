var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var ColdcallActions = require('../../action/ColdcallActions');

var Functions = require('../../../../react-kit/util/Functions');


const ColdcallCandidates = React.createClass({


    render(){
        var data = this.props.data;
        if( data.candidates == null ){
            return null;
        }

        return(
            <div>
                { data.candidates.map(function (result, index) {
                    var flag = false;
                    if(data.companies != null) {
                        for (var i = 0; i < data.companies.length; i++) {
                            var company = data.companies[i]
                            if (company.code == result.code) {
                                flag = true;
                                break;
                            }
                        }
                    }
                    return <ListElement key={index} data={result} flag={flag}/>;
                }.bind(this))}

            </div>
        )
    }

});

const ListElement = React.createClass({
    render(){
        if(this.props.flag) return null;

        var data = this.props.data;
        //console.log(this.props.flag);
        var selectLink = <i className="fa fa-check m-r-10 text-navy"></i>;
        if(this.props.flag == false){
            selectLink = <a onClick={this.clickChoose}>
                            <i className="fa fa-plus m-r-10 add-match"></i>
                        </a>
        }
        return(
            <div className="candidate-item">
                {selectLink}
                <a href={"/#/company/" + data.code + "/overview"} _blank>{data.name}(候选)</a>
            </div>
        )
    },
    clickChoose() {
        var code = this.props.data.code;
        console.log("choose " + code);
        ColdcallActions.select(code);
    }
});

module.exports = ColdcallCandidates;

