var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SearchStore = require('../../store/SearchStore');
var SearchActions = require('../../action/SearchActions');

var MobileSearchResult = require('./MobileSearchResult.react');

var Functions = require('../../../../react-kit/util/Functions');
var View = require('../../../../react-kit/util/View');
var Loading = require('../../../../react-kit/basic/Loading.react');


const MobileSearch = React.createClass({
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

        var type = this.props.type;
        if(type == 'latest'){
            searchNav = null;
        }

        return (
            <div className="search-body main-body">
                <div className="search-main">
                    <MobileSearchResult data={data} />
                </div>
            </div>
        );

    },

    scroll(){
        if(View.bottomLoad(100)){
            SearchActions.loadMore();
        }
    }


});


module.exports = MobileSearch;

