var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var DemoDayActions = require('../../action/demoday/DemoDayActions');
var DemoDayStore = require('../../store/demoday/DemoDayStore');
var Functions = require('../../../../react-kit/util/Functions');
var DemoDayUtil = require('../../util/DemoDayUtil');
var DemoDayNav = require('./DemoDayNav.react');
var PreScores = require('./list/PreScores.react');
var Scores =require('./list/Scores.react');
var AddItem = require('./add/AddItem.react');
var NOPassList = require('./NoPassList.react');
var Loading = require('../../../../react-kit/basic/Loading.react');

var SearchCompanyStore = require('../../../../react-kit/store/SearchCompanyStore');

const DemoDay = React.createClass({

    mixins: [Reflux.connect(DemoDayStore, 'data'),
             Reflux.connect(SearchCompanyStore, 'search')],

    componentWillMount() {
        DemoDayActions.getDemoDay(this.props.id);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.id == nextProps.id) return;
        DemoDayActions.getDemoDay(nextProps.id);
    },

    render(){
        if(Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;
        if(!data.firstLoad){
            return <Loading />
        }
        var id = data.id;
        var demoday = data.selectedDemoDay.demoday;
        var companies = data.companies;
        var hint = true;

        var searchList = [];
        if(this.state.search != null){
            searchList = this.state.search.list;
        }

        var createLink = "/#/demoday/"+data.id+"/create";
        var leftClass = "column three-fourths";
        var rightClass = "column one-fourth dd-submit-item ";

        var status = data.status;
        if(status == 26000){
            rightClass += 'show';
        }else{
            leftClass = "all-block";
            rightClass = 'hide'
        }

        var scoreList;

        if(status == 26000 || status == 26010 || status == 26020){
            scoreList = <PreScores list={companies} id={id} />
        }else{
            scoreList = <Scores list={companies} id={id} />
        }


        return(
            <div className="main-body dd-body">

                <div className={leftClass}>
                    <DemoDayNav selected="demoday"
                                hint ={hint}
                                id={id} />

                    <div className="dd-detail-list">
                        {scoreList}
                    </div>

                    <NOPassList data={data}/>

                </div>

                <div className={rightClass}>
                    <AddItem companies={companies} searchList={searchList}/>

                    <div className="m-t-15">
                        <div className="dd-submit-hint">没有搜索到？请新建公司后提交</div>
                        <a className="a-button" href={createLink}>
                            <i className="fa fa-plus fa-xl m-r-5"></i>新建项目
                        </a>
                    </div>
                </div>

            </div>
        )
    }

});




module.exports = DemoDay;

