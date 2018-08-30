var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var MytaskStore = require('../../store/MytaskStore');
var MytaskActions = require('../../action/MytaskActions');
var Functions = require('../../../../react-kit/util/Functions');
var View = require('../../../../react-kit/util/View');
var Loading = require('../../../../react-kit/basic/Loading.react');

var SelfList = require('./list/SelfList.react.js');
var UserHome = require('../user/UserHome.react');


const Discovery = React.createClass({

    mixins: [Reflux.connect(MytaskStore, 'data')],

    componentWillMount() {
        MytaskActions.getDiscovery(this.props.status);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.status == nextProps.status) return;
        MytaskActions.getDiscovery(nextProps.status);
    },

    componentDidMount(){
        window.addEventListener('scroll', this.scroll);
    },

    componentWillUnmount(){
        window.removeEventListener('scroll', this.scroll);
    },

    render(){
        if(Functions.isEmptyObject(this.state))
            return null;

        var data= this.state.data;
        if(!data.firstLoad) {
            return <Loading />;
        }

        var loading;
        if(data.loading)
            loading = <Loading />;

        if(this.props.from == 'mobile'){
            return (
                <div className="m-body">
                    <UserHome type='discovery' from="mobile"/>
                    <DiscoveryDetails data={data}/>
                    {loading}
                </div>
            )
        }

        return(
            <div className="main-body">
                <div className="page-title">我的发现</div>
                <div className="column three-fourths">
                    <DiscoveryDetails data={data}/>
                    {loading}
                </div>
                <div className="column one-fourth user-part">
                    <UserHome type='discovery'/>
                </div>
            </div>
        )
    },

    scroll(){
        if(View.bottomLoad(100)){
            MytaskActions.listMore(23010);
        }
    }

});


const DiscoveryDetails = React.createClass({
    render(){
        var data = this.props.data;
        var list = data.list_self;
        var count = data.cnt_total_self;

        return(
            <div>
                <DiscoveryFilter data={data} count={count}/>
                <SelfList list={list} count={count} />
            </div>
        )
    }
});

const DiscoveryFilter = React.createClass({
    render(){
        var data = this.props.data;
        var status = data.filter_self;

        return(
            <div className="task-filter-bar">
                <div>
                    <FilterStatus selected={status} type="999" name="全部" />
                    <FilterStatus selected={status} type="4" name="重点跟进" />
                    <FilterStatus selected={status} type="3" name="随便聊聊" />
                    <FilterStatus selected={status} type="2" name="太烂了" />
                    <FilterStatus selected={status} type="1" name="不关心" />
                </div>
                <div className="task-count-right">
                    <strong>{this.props.count}</strong> 个发现
                </div>
            </div>

        )
    }
});


const FilterStatus = React.createClass({
    render(){
        var className;
        if(this.props.selected == this.props.type){
            className = 'active';
        }
        return(
            <a className={className} onClick={this.click}>{this.props.name}</a>
        )
    },
    click(){
        MytaskActions.changeDiscoveryFilterStatus(this.props.type)
    }
});



module.exports = Discovery;