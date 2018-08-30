var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../react-kit/util/Functions');
var CollectionStore = require('../../store/collection/CollectionStore');
var CollectionActions = require('../../action/collection/CollectionActions');

var CollectionTimeline= require('./CollectionTimeline.react');
var CollectionList = require('./CollectionList.react');
var View = require('../../../../react-kit/util/View');

const Collection = React.createClass({

    mixins: [Reflux.connect(CollectionStore, 'data')],

    componentWillMount(){
        CollectionActions.init();
    },

    componentWillReceiveProps(nextProps){
        CollectionActions.init();
        //if(this.props.coldcallId == nextProps.coldcallId) return;
        //ColdcallActions.init(nextProps.coldcallId);
    },
    componentDidMount(){
        window.addEventListener('scroll', this.scroll);
    },

    componentWillUnmount(){
        window.removeEventListener('scroll', this.scroll);
    },
    render(){
        if (Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;

        return(
            <div>
                <div className="column three-fourths left-block">
                    <CollectionTimeline data={data} />
                </div>

                <div className="column one-fourth ">
                    <CollectionList data={data}/>
                </div>
            </div>
        )
    },
    scroll(){
        if(View.bottomLoad(100)){
            CollectionActions.listMore();
        }
    }

});





module.exports = Collection;

