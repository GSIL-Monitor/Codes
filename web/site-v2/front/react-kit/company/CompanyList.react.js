var React = require('react');
var $ = require('jquery');

var CompanyInfo = require('./CompanyInfo.react');
var SectorList = require('./SectorList.react');
var TagList = require('./TagList.react');
var DivExtend = require('../basic/DivExtend.react');
var Functions = require('../util/Functions');

var CompanyUtil = require('../../webapp-site/js/util/CompanyUtil');

const CompanyList = React.createClass({
    render(){
       var list = this.props.data;
       if(list == null) return null;
       if(list.length == 0) return null;

       var more;
       if(this.props.more != null){
           var len = 5;
           if(list.length > len){
               list = CompanyUtil.getSubList(list, len, this.props.more);
               if(this.props.more){
                   more = <DivExtend type="less" extend={this.extend}/>
               }
               else{
                   more = <DivExtend type="more" extend={this.extend}/>
               }
               more = <div className="all-block m-t-10">
                           {more}
                       </div>
           }
       }

       return(
            <div className="company-list">
                {list.map(function (result, index) {
                    return <ListElement key={index} data={result}/>;
                }.bind(this))}

                {more}
            </div>
       )
    },

    extend(){
        this.props.extend();
    }
});


const ListElement = React.createClass({

    render(){
        var data = this.props.data;
        var descClass = "item-description ";
        if (this.state != null){
            if(this.state.selected)
                descClass = descClass+"auto-height";
        }

        var roundName = Functions.getRoundName(data.round);

        var establishDate = data.establishDate;
        if(establishDate != null){
            establishDate = establishDate.substring(0,7);
        }

        var location = data.location;
        if(location != null){
            location = "@"+location;
        }

        return(
            <div className="search-list-item" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>

                <div className="item-head">
                    <CompanyInfo className="item-name" code={data.code} name={data.name}/>
                    <span className="item-round">{roundName}</span>
                    <SectorList data={data.sectors} />
                    <TagList data={data.tags} />
                </div>

                <div className={descClass}>{data.description}</div>
                <div className="item-meta">{establishDate} {location}</div>
            </div>
        )
    },

    onMouseOver(){
        this.setState({selected: true})
    },

    onMouseOut(){
        this.setState({selected: false})
    }

});

module.exports = CompanyList;