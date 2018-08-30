var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var NewsStore = require('../../../store/company/NewsStore');
var NewsActions = require('../../../action/company/NewsActions');
var CompanyUtil = require('../../../util/CompanyUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var DivExtend = require('../../../../../react-kit/basic/DivExtend.react');

const News = React.createClass({
    mixins: [Reflux.connect(NewsStore, 'data')],

    componentWillMount() {
        NewsActions.get(this.props.id);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.id == nextProps.id) return;
        NewsActions.get( nextProps.id);
    },

    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;

        var data = state.data.list;
        if(data == null) return null;
        if(data.length ==0) return null;

        var showAll = this.state.data.showAll;

        var more;
        var len = 6;
        if(data.length > len){
            data = CompanyUtil.getSubList(data, len, showAll);
            if(showAll){
                more = <DivExtend type="less" extend={this.extend}/>
            }
            else{
                more = <DivExtend type="more" extend={this.extend}/>
            }
        }

        return (
            <div className="section m-b-20">
                <span className="section-header">
                    相关报道
                </span>
                <section className="section-body">
                    <ol className="vertical-timeline">
                        {data.map(function (result, index) {
                                return <NewsItem key={index} data={result}/>;
                        })}
                    </ol>
                    <div className="news-extend">{more}</div>

                    </section>
            </div>

        )
    },

    extend(){
        NewsActions.showAll();
    }

});


const NewsItem = React.createClass({
    render(){
        var data = this.props.data;
        var date = data.date;
        if(Functions.isNull(date)){
            date = 'N/A'
        }
        return (
            <li className="tl-node" >
                <div className="news-item-body">
                    <div className="news-title" onClick={this.click}>

                        <div className="news-time">
                            {date}
                        </div>
                        <div className="news-name">
                            {data.title}
                        </div>

                    </div>
                </div>
            </li>
        )
    },

    click(){
        var data = this.props.data;
        var link = './#/news/'+data.companyId+'/'+data.id;
        window.open(link)
    }
});


module.exports = News;