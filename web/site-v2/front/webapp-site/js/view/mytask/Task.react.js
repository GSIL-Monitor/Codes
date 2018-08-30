var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var MytaskStore = require('../../store/MytaskStore');
var MytaskActions = require('../../action/MytaskActions');
var Functions = require('../../../../react-kit/util/Functions');
var View = require('../../../../react-kit/util/View');
var Loading = require('../../../../react-kit/basic/Loading.react');

var TaskList = require('./list/TaskList.react.js');
var UserHome = require('../user/UserHome.react');


const Task = React.createClass({

    mixins: [Reflux.connect(MytaskStore, 'data')],

    componentWillMount() {
        MytaskActions.getTask(this.props.type, this.props.status);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.type == nextProps.type && this.props.status == nextProps.status) return;
        MytaskActions.getTask(nextProps.type, nextProps.status);
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
                    <UserHome type='task' from="mobile"/>
                    <TaskDetails data={data}/>
                    {loading}
                </div>
            )
        }

        return(
            <div className="main-body">
                <div className="page-title">我的任务</div>
                <div className="column three-fourths">
                    <TaskDetails data={data}/>
                    {loading}
                </div>
                <div className="column one-fourth user-part">
                    <UserHome type='task'/>
                </div>
            </div>
        )
    },

    scroll(){
        if(View.bottomLoad(100)){
            MytaskActions.listMore(1);
        }
    }

});


const TaskDetails = React.createClass({
    render(){
        var data = this.props.data;
        var list = data.list_task;
        var count = data.cnt_total_task;

        return(
            <div>
                <MyTaskFilter data={data} count={count}/>
                <TaskList list={list} count={count} />
            </div>
        )
    }
});


const MyTaskFilter = React.createClass({
    render(){
        var data = this.props.data;
        var filterType = data.filter_task_type;
        var filterStatus = data.filter_task;

        return(
            <div className="task-filter-bar">
                <div>
                    <FilterType selected={filterType} type="all" name="全部"/>
                    <FilterType selected={filterType} type="coldcall" name="Cold Call"/>
                    <FilterType selected={filterType} type="system" name="系统分配"/>
                </div>
                <div>
                    <FilterStatus selected={filterStatus} type="999" name="全部" />
                    <FilterStatus selected={filterStatus} type="0" name="待处理" />
                    <FilterStatus selected={filterStatus} type="4" name="重点跟进" />
                    <FilterStatus selected={filterStatus} type="3" name="随便聊聊" />
                    <FilterStatus selected={filterStatus} type="2" name="太烂了" />
                    <FilterStatus selected={filterStatus} type="1" name="不关心" />
                </div>
                <div className="task-count-right">
                    <strong>{this.props.count}</strong> 个任务
                </div>
            </div>

        )
    }
});


const FilterType = React.createClass({
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
        MytaskActions.changeTaskFilterType(this.props.type)
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
        MytaskActions.changeTaskFilterStatus(this.props.type)
    }
});



module.exports = Task;

