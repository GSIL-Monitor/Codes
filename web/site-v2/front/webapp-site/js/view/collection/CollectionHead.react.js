var React = require('react');
var $ = require('jquery');

var CollectionActions = require('../../action/collection/CollectionActions');

const CollectionHead = React.createClass({

    render(){
        var name = this.props.name;
        var data = this.props.data;
        var filterTags = data.filterTags;
        var filterLocations = data.filterLocations;
        var filterRounds = data.filterRounds;

        return(
           <div className="collection-head">
               <div className="selected-collection-name">{name}</div>
               <div className="selected-filter-list">
                   <SelectedFilterList list={filterTags} type="tag" />
                   <SelectedFilterList list={filterLocations} type="location" />
                   <SelectedFilterList list={filterRounds} type="round" />
               </div>

               <div className="collection-head-filter">
                   <a onClick={this.filter}>筛选</a>
               </div>
           </div>
        )
    },

    filter(){
        $('#collection-filter-modal').show();
    }

});

var SelectedFilterList = React.createClass({
    render(){
        var list = this.props.list;
        var type = this.props.type;
        if(list.length == 0) return null;
        return(
            <div>
                {list.map(function(result, index){
                    return <SelectedFilterItem data={result} key={index} type={type}/>
                }.bind(this))}
            </div>
        )
    }
});


var SelectedFilterItem = React.createClass({

    getInitialState: function() {
        return {selected: false};
    },

    render(){
        var data = this.props.data;
        var type = this.props.type;
        var typeName;
        if(type == 'tag'){
            typeName = '标签';
        }else if(type == 'location'){
            typeName = '地点';
        }else if(type == 'round'){
            typeName = '轮次';
        }

        var change;
        if(this.state.selected)
            change = true;

        if(change) {
            return (
                <div className="selected-filter-item"
                     onMouseEnter={this.onMouseEnter}
                     onMouseLeave={this.onMouseLeave}>
                    {typeName}: {data.name}
                    <span className="delete-icon" onClick={this.delete}>
                        <i className="fa fa-times fa-lg"></i>
                    </span>
                </div>
            )
        }

        return(
            <div className="selected-filter-item"
                 onMouseEnter={this.onMouseEnter}
                 onMouseLeave={this.onMouseLeave}>
                {typeName}: {data.name}

            </div>
        )

    },

    onMouseEnter(){
        this.setState({selected: true})
    },

    onMouseLeave(){
        this.setState({selected: false})
    },

    delete(){

    }
});

module.exports = CollectionHead;