var React = require('react');
var $ = require('jquery');

var CompanyListStore = require('../../store/home/CompanyListStore');
var CompanyListAction = require('../../action/home/CompanyListAction');

var Functions = require('../../util/Functions');

const CompanyList = React.createClass({

    componentDidMount() {
        var data={ids: '881,882,883'};

        CompanyListAction.get(data.ids);
        CompanyListStore.addChangeListener(this._onChange);
    },

    componentWillUnmount(){
        CompanyListStore.removeChangeListener(this._onChange);
    },


    render() {

        var state = this.state;
        if(state == null){
            return null;
        }else{

        return (
            <div>
                <div className="list-head">
                    <div className="basic">公司</div>
                    <div className="desc">简介</div>
                    <div className="funding">融资</div>
                    <div className="location">地点</div>
                    <div className="date">创立时间</div>
                    <div className="last"></div>
                </div>


                { this.state.list.map(function(result){
                    return  <Company  key={result.id}  data={result} />;
                }.bind(this))}
            </div>

        );
        }
    },

    _onChange(){
        this.setState({list:CompanyListStore.get()})
    }
});


var Company = React.createClass({
    render(){
        var data = this.props.data;
        var link = "#/company/basic/"+data.id;

        var roundName = Functions.getRoundName(data.round);

        return(
            <div className="list-element">
                <div className="basic">
                    <div className="name"><a href={link}>{data.name}</a></div>
                    <div>{data.brief}</div>
                </div>
                <div className="desc">{data.description}</div>
                <div className="funding">{roundName}</div>
                <div className="location">{data.location}</div>
                <div className="date">{data.establishDate}</div>
                <div className="last">{data.roundDesc}</div>
            </div>
        )
    }
})


module.exports = CompanyList;

