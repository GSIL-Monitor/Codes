var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../react-kit/util/Functions');
var ColdcallStore = require('../../store/ColdcallStore');
var ColdcallActions = require('../../action/ColdcallActions');
var ColdcallDetail = require('./ColdcallDetail.react');
var ColdcallCompanies = require('./ColdcallCompanies.react.js');
var ColdcallCandidates = require('./ColdcallCandidates.react.js');
var ColdcallSearch = require('./ColdcallSearch.react.js');
var CreateCompanyStore = require('../../store/CreateCompanyStore');

var SearchCompanyStore = require('../../../../react-kit/store/SearchCompanyStore');

var Forward = require('./Forward.react.js');

const Coldcall = React.createClass({

    mixins: [Reflux.connect(ColdcallStore, 'data'),
            Reflux.listenTo(CreateCompanyStore, "onCreateCompanyChange"),
            Reflux.connect(SearchCompanyStore, 'searchMatch')],

    onCreateCompanyChange(store) {
        if (store.saved == true) {
            $('#cc-create-company-modal').hide();
            var coldcallId = parseInt(this.props.coldcallId);
            ColdcallActions.getCompanies(coldcallId);
        }
    },

    componentWillMount(){
        ColdcallActions.init(this.props.coldcallId);
    },

    componentWillReceiveProps(nextProps){
        if(this.props.coldcallId == nextProps.coldcallId) return;
        ColdcallActions.init(nextProps.coldcallId);
    },

    render(){
        if (Functions.isEmptyObject(this.state))
            return null;

        var data = this.state.data;

        if(this.props.from == 'mobile'){
            return  <ColdcallDetail data={data} />
        }

        var searchMatches = [];
        var matchList = [];
        var searchList = [];
        if(this.state.searchMatch != null){
            searchMatches = this.state.searchMatch.matches;
            searchList = this.state.searchMatch.list;
        }

        var leftClass = 'coldcall-left ';
        var rightClass = 'coldcall-right m-t-10 ';

        var arrow;
        //if(data.extend){
        //    arrow = <i className="fa fa-angle-double-right fa-lg"></i>;
        //    leftClass = 'coldcall-left coldcall-left-small';
        //    rightClass = 'coldcall-right m-t-10 coldcall-right-large';
        //}
        //else{
            arrow = <i className="fa fa-angle-double-left fa-lg"></i>;
            leftClass = 'coldcall-left';
            rightClass = 'coldcall-right m-t-10';
        //}

        //<span className="cc-extend"
        //      onMouseOver={this.onMouseOver}
        //      onMouseOut={this.onMouseOut}
        //      onClick={this.click} >
        //                {arrow}
        //</span>

        return(
            <div>
                <div className={leftClass}>
                    <ColdcallDetail data={data} />
                </div>
                <div className={rightClass}>


                    <div>
                        <ColdcallCompanies data={data} />
                    </div>

                    <div>
                        <ColdcallCandidates data={data} />
                    </div>

                    <div className="cc-search">
                        <ColdcallSearch data={data} list={searchList}/>
                    </div>

                    <div>
                        <div className="cc-match-hint m-t-20 m-b-5">搜不到？可以自己添加公司：</div>
                        <a className="a-button" href={"/#/coldcall/"+parseInt(this.props.coldcallId)+"/company/create"}
                            target='_blank'>
                            <i className="fa fa-plus fa-xl m-r-5"></i>新建公司
                        </a>
                    </div>

                    <ColdcallDecline data={data}/>

                </div>
            </div>
        )
    },

    onMouseOver(){

    },

    onMouseOut(){

    },

    click(){
        ColdcallActions.extend();
    }

});

const ColdcallDecline = React.createClass({
    render(){
        var data = this.props.data;

        return(
            <div>
                <div className="cc-match-hint m-t-20 m-b-5">项目不在我的关注范围内</div>

                <Forward data={data}/>

            </div>
        )
    },

    click(){
        $('#coldcall-forward-modal').show();
    }
});

//const DeclineItem = React.createClass({
//    render(){
//        return(
//            <div>
//                <a className={this.props.className} onClick={this.decline}>{this.props.name}</a>
//            </div>
//        )
//    },
//
//    decline(){
//        ColdcallActions.decline(this.props.id);
//    }
//});






module.exports = Coldcall;

