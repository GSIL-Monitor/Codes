var React = require('react');
var Reflux = require('reflux');

var Functions = require('../../../../../react-kit/util/Functions');
var NewCollectionStore = require('../../../store/collection/NewCollectionStore');
var NewCollectionActions = require('../../../action/collection/NewCollectionActions');

var EstablishDateFilters = require('../filter/EstablishDateFilters.react');
var InvestorFilters = require('../filter/InvestorFilters.react');
var LocationFilters = require('../filter/LocationFilters.react');
var RoundFilters = require('../filter/RoundFilters.react');
var TagFilters = require('../filter/TagFilters.react');
var TeamBackgroundFilters = require('../filter/TeamBackgroundFilters.react');


const NewCollection = React.createClass({

    mixins: [Reflux.connect(NewCollectionStore, 'data')],

    componentWillMount(){
        NewCollectionActions.init();
    },

    componentWillReceiveProps(nextProps){
        //if(this.props.coldcallId == nextProps.coldcallId) return;
        //ColdcallActions.init(nextProps.coldcallId);
    },

    render(){
        if (Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;

        return(
            <div className="main-new-collection">
                <div className="new-collection-title">自定义集合</div>
                <TagFilters data={data}/>
                <LocationFilters data={data}/>
                <RoundFilters data={data} />
                <TeamBackgroundFilters data={data}/>
                <InvestorFilters data={data}/>
                <EstablishDateFilters data={data}/>
                <CollectionName data={data}/>

                <AddCollection />
            </div>
        )
    }

});


const CollectionName = React.createClass({
    render(){
        var data = this.props.data;
        var value = data.name;
        return (
            <div className="collection-form">

                <div className="collection-form-left">
                    <span className='left-required'>*</span>
                    <span>集合名称</span>
                </div>

                <div className="collection-form-right">
                    <input type="text" value={value} onChange={this.change}/>
                </div>

            </div>
        )
    },
    change(e){
        NewCollectionActions.changeName(e.target.value);
    }
});


const AddCollection = React.createClass({
    render(){
       return(
           <div>
               <button className="btn btn-navy btn-collection-add" onClick={this.add}>创建集合</button>
           </div>
       )
    },
    add(){
        NewCollectionActions.add();
    }
});


module.exports = NewCollection;

