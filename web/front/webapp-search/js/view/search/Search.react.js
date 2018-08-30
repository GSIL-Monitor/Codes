var React = require('react');
var $ = require('jquery');

var SearchStore = require('../../store/SearchStore');
var SearchAction = require('../../action/SearchAction');

var SearchNav = require('./SearchNav.react.js');
var SearchAside = require('./SearchAside.react.js');
var SortBar = require('./SortBar.react.js');

var Config = require('../../../../react-kit/util/Config');
var Functions = require('../../../../react-kit/util/Functions');

const Search = React.createClass({

    componentDidMount() {
        var data={ids: '881,882,883'};

        SearchAction.get(data.ids);
        SearchStore.addChangeListener(this._onChange);
    },

    componentWillUnmount(){
        SearchStore.removeChangeListener(this._onChange);
    },

    render() {
        var state = this.state;

        if(state == null){
            return null;
        }
        else if(state.list.length == 1){
            return(
                <div>
                    <SearchResult data={this.state.list} />
                </div>
            )
        }
        else{
            return (
                <div>
                    <SearchNav value={this.state.search} onChange={this.handleChange} />

                    <div>
                        <SearchAside />
                        <SearchResult data={this.state.list} sort={this.state.sort} className="column three-fourths"/>
                    </div>
                </div>
            );
        }
    },

    handleChange(value){
        SearchAction.changeSearchInput(value);
    },

    _onChange(){
        this.setState({list:SearchStore.get()});
        this.setState({sort: SearchStore.getSort()});
        this.setState({search: SearchStore.getSearch()});
    }

});




const SearchResult = React.createClass({
    render(){

        return (
            <div className={this.props.className}>
                <SortBar count={this.props.data.length} sort={this.props.sort}/>

                <div>
                    { this.props.data.map(function (result) {
                        return <ListElement key={result.id} data={result}/>;
                    }.bind(this))}

                </div>
            </div>
        )
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
        var link = Config.preURLDirectToSite()+"#/company/"+data.code+"/overview";

        return(
            <div className="search-list-item" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                <div className="right item-field">
                    Saas
                </div>
                <div className="item-head">
                    <a className="item-name" href={link} target="_blank">{data.name}</a>
                    <span className="m-l-10 m-r-20">{roundName}</span>
                    <span className="tag">
                        团队
                    </span>
                    <span className="tag">
                        团队
                    </span>
                    <span className="tag">
                        团队
                    </span>

                </div>
                <div className={descClass}>{data.description}</div>
                <div className="item-meta">{data.establishDate}  @{data.location}</div>
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



module.exports = Search;

