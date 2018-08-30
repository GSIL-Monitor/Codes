var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../store/CompanyStore');
var CompanyActions = require('../../action/CompanyActions');

var Header = require('./basic/CompanyHeader.react.js');
var Basic = require('./basic/CompanyBasic.react.js');
var Product = require('./product/Product.react.js');
var Member = require('./team/Member.react.js');
var Recruit = require('./team/Recruit.react.js');
var Data = require('./data/Data.react.js');
var News = require('./news/News.react.js');
var CompsCtrl = require('./comps/CompsCtrl.react');

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
            return <div className="all-block"></div>;
        }else if(this.state.data.company == null){
            return <div className="all-block"></div>;
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
            if(from == 'complete'){
                title = 'Demo Day提交项目 -' + title;
            }

            Functions.updateTitle('title', title);

            return (
                <div>

                    <Header data={data}/>
                    <Basic data={data}/>

                    <Product id={id} />
                    <Member id={id} />
                    <Recruit id={id} />
                    <News id={id} />

                    <CompsCtrl id={id} />

                </div>

            );
        }
    }

});







module.exports = Overview;

