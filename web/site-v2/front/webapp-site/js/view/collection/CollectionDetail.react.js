var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../react-kit/util/Functions');
var CollectionStore = require('../../store/collection/CollectionStore');
var CollectionActions = require('../../action/collection/CollectionActions');

var CollectionCompanies= require('./CollectionCompanies.react');
var CollectionList = require('./CollectionList.react');
var View = require('../../../../react-kit/util/View');

const Collection = React.createClass({

    mixins: [Reflux.connect(CollectionStore, 'data')],

    componentWillMount(){
        CollectionActions.getCollection(this.props.collectionId);
    },

    componentWillReceiveProps(nextProps){
        if(this.props.collectionId == nextProps.collectionId) return;
        CollectionActions.getCollection(nextProps.collectionId);
    },

    componentDidMount(){
        window.addEventListener('scroll', this.scroll);
    },

    componentWillUnmount(){
        window.removeEventListener('scroll', this.scroll);
    },

    scroll(){
        if(View.bottomLoad(100)){
            CollectionActions.listMore(this.state.data.collectionId);
        }
    },

    render(){
        if (Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;
        var list = data.timeline;
        var collection = data.collection;

        return(
            <div>
                <div className="column three-fourths left-block">
                    <CollectionCompanies list={list} collection={collection}/>
                </div>

                <div className="column one-fourth">
                    <CollectionList data={data}/>
                </div>
            </div>
        )
    }

});





module.exports = Collection;

