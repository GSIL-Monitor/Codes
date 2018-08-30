var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../react-kit/util/Functions');
var CommonSearchActions = require('../../../../../react-kit/action/SearchActions');

const SearchType = React.createClass({
    render(){
        var id = 0;
        var data = [{type:'company', count: 1001}, {type:'keyword', count: 1}]


        return(
            <nav className="menu">
                { data.map(function (result) {
                    id++;
                    return <TypeElement key={id} data={result} type={this.props.type}/>;
                }.bind(this))}


            </nav>
        )
    }
});


const TypeElement = React.createClass({

    render(){
        var className= "menu-item";

        if(this.props.data.type == this.props.type){
            className += " selected";
        }

        var iClassName = "fa ";
        var type;
        if(this.props.data.type == 'company'){
            iClassName += "fa-building";
            type = '公司'
        }else if(this.props.data.type == 'keyword'){
            iClassName += "fa-tag";
            type = '标签'
        }

        return(
            <a className={className} onClick={this.click}>

                <span className="octicon">
                    <i className={iClassName}></i>
                </span>

                {type}

                <span className="counter" >
                    {this.props.data.count}
                </span>

            </a>
        )
    },

    click(){
        CommonSearchActions.clickSearch(this.props.data.type, search);
    }

});

module.exports = SearchType;