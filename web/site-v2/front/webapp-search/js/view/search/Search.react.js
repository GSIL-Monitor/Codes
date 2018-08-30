var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SearchStore = require('../../store/SearchStore');
var SearchActions = require('../../action/SearchActions');

var SearchNav = require('./SearchNav.react.js');
var SearchResult = require('./SearchResult.react');
var SearchAside = require('./SearchAside.react.js');

var Functions = require('../../../../react-kit/util/Functions');
var View = require('../../../../react-kit/util/View');
var Loading = require('../../../../react-kit/basic/Loading.react');


const Search = React.createClass({
    mixins: [Reflux.connect(SearchStore, 'data')],

    componentWillMount() {
        SearchActions.search(this.props.type, this.props.value);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.type == nextProps.type && this.props.value == nextProps.value) return;
        SearchActions.search(nextProps.type, nextProps.value);
    },

    componentDidMount(){
        window.addEventListener('scroll', this.scroll);
    },

    componentWillUnmount(){
        window.removeEventListener('scroll', this.scroll);
    },


    render() {
        if(Functions.isEmptyObject(this.state)){
            return null;
        }

        var data = this.state.data;
        if(!data.firstLoad)
            return <Loading />;


        var searchNav = <SearchNav value={data.search}
                                   type={data.type}
                                   onChange={this.handleChange}/>;

        var type = this.props.type;
        if(type == 'latest'){
            searchNav = null;
        }

        return (
            <div className="search-body main-body">
                {searchNav}

                <div className="search-main">
                    <SearchAside data={data}/>
                    <SearchResult data={data}
                                  className="column three-fourths"/>

                </div>
            </div>
        );

    },

    handleChange(value){
        SearchActions.changeSearch(value);
    },

    scroll(){
        if(View.bottomLoad(100)){
            SearchActions.loadMore();
        }
    }


});



module.exports = Search;

