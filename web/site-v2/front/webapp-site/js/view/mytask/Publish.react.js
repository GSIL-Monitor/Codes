var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var MytaskStore = require('../../store/MytaskStore');
var MytaskActions = require('../../action/MytaskActions');
var Functions = require('../../../../react-kit/util/Functions');
var View = require('../../../../react-kit/util/View');
var Loading = require('../../../../react-kit/basic/Loading.react');

var PublishTaskList = require('./list/PublishList.react.js');
var UserHome = require('../user/UserHome.react');


const Publish = React.createClass({

    mixins: [Reflux.connect(MytaskStore, 'data')],

    componentWillMount() {
        MytaskActions.getPublishTask(this.props.status);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.status == nextProps.status) return;
        MytaskActions.getPublishTask(nextProps.status);
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
                    <UserHome type='publish' from="mobile"/>
                    <PublishDetails data={data}/>
                    {loading}
                </div>
            )
        }


        return(
            <div className="main-body" onScroll={this.scroll}>
                <div className="page-title">发布的任务</div>
                <div className="column three-fourths">
                    <PublishDetails data={data}/>
                    {loading}
                </div>
                <div className="column one-fourth user-part">
                    <UserHome type='publish'/>
                </div>
            </div>
        )
    },

    scroll(){
        if(View.bottomLoad(100)){
            MytaskActions.listMore(2);
        }
    }

});


const PublishDetails = React.createClass({
    render(){
        var data = this.props.data;
        var list = data.list_sponsoredcoldcall;
        var count = data.cnt_total_sponsoredcoldcall;

        return(
            <div>
                <PublishFilter data={data} count={count}/>
                <PublishTaskList list={list} count={count} />
            </div>
        )
    }
});

const PublishFilter = React.createClass({
    render(){
        var data = this.props.data;
        var status = data.filter_sponsoredcoldcall;

        return(
            <div className="task-filter-bar">
                <div>
                    <FilterStatus selected={status} type="999" name="全部" />
                    <FilterStatus selected={status} type="0" name="待处理" />
                    <FilterStatus selected={status} type="4" name="重点跟进" />
                    <FilterStatus selected={status} type="3" name="随便聊聊" />
                    <FilterStatus selected={status} type="2" name="太烂了" />
                    <FilterStatus selected={status} type="1" name="不关心" />
                </div>
                <div className="task-count-right">
                    <strong>{this.props.count}</strong> 个任务
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
        MytaskActions.changePublishFilterStatus(this.props.type)
    }
});



module.exports = Publish;