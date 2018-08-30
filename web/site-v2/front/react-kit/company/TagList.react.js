var React = require('react');
var Functions = require('../../react-kit/util/Functions');

const TagList = React.createClass({

    render(){
        if(Functions.browserVersion() == 'mobile')
            return null;

        var data = this.props.data;
        if(data == null) return null;
        if(data.length == 0) return null;


        if(data.length > 5){
            var subs = [];
            for(var i=0; i<5; i++){
                subs.push(data[i]);
            }
            data = subs;
        }

        var className = this.props.className;
        if(className == null){
            className = "label tag light-tag";
        }

        return(
            <span className="search-tag-list">
                {data.map(function(result, index){
                    return <TagItem key={index} data={result.name} className={className} />
                }.bind(this))}
            </span>
        )
    }
});


const TagItem = React.createClass({

    render(){
        return(
            <span className= {this.props.className}
                  onClick={this.click}>
               {this.props.data}
            </span>
        )
    },

    click(){
        window.location.href = '/search/#/open/'+this.props.data;
    }
});

module.exports = TagList;