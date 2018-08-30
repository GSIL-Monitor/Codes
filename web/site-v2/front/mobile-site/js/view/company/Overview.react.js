var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../../webapp-site/js/store/CompanyStore');
var CompanyActions = require('../../../../webapp-site/js/action/CompanyActions');

var Header = require('./basic/Header.react.js');
var Basic = require('./basic/Basic.react.js');
var Product = require('./product/Product.react.js');
var Member = require('./team/Member.react.js');
var Recruit = require('./team/Recruit.react.js');
var News = require('../../../../webapp-site/js/view/company/news/News.react.js');
var Comps = require('./comps/Comps.react');

var Functions = require('../../../../react-kit/util/Functions');

const Overview = React.createClass({

    mixins: [Reflux.connect(CompanyStore, 'data')],

    componentWillMount() {
        CompanyActions.init(this.props.code, this.props.from, this.props.id);
    },

    componentWillReceiveProps(nextProps) {
        if( this.props.code == nextProps.code &&
            this.props.from == nextProps.from &&
            this.props.id == nextProps.id)
            return;
        CompanyActions.init(nextProps.code, nextProps.from, nextProps.id);
    },


    render() {
        if(Functions.isEmptyObject(this.state)){
            return null;
        }else if(this.state.data.company == null){
            return null;
        }else{
            var data = this.state.data;
            var id = data.companyId;
            var from = data.from;

            var title = this.state.data.company.name;
            if(from == 'preScore'){
                title = '预筛选打分 - '+ title;
            }
            if(from == 'score'){
                title = '打分 - '+ title;
            }

            Functions.updateTitle('title', title);

            //
            //<Product id={id} />
            //
            //
            return (
                <div className="all-block">

                    <Header data={data}/>
                    <Basic data={data}/>

                    <Member id={id} />
                    <Recruit id={id} />
                    <News id={id} />
                    <Comps id={id} />

                </div>

            );
        }
    }

});







module.exports = Overview;

