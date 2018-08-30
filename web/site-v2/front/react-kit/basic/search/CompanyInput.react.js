var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../store/SearchCompanyStore');
var CompanyActions = require('../../action/SearchCompanyActions');

var Functions = require('../../util/Functions');

var CompanyInput = React.createClass({
    mixins: [Reflux.connect(CompanyStore, 'data')],

    componentWillMount() {
        CompanyActions.init(this.props.from, this.props.demodayId);
    },

    componentWillReceiveProps(nextProps) {
        //CompanyActions.init(nextProps.from, nextProps.demodayId);
    },

    render() {
        var hint = null;
        var selected = null;

        if(Functions.isEmptyObject(this.state)){
            return <input type="text" className="search-company-input" placeholder="通过产品名/公司名查找" />
        }

        var value = this.state.data.value;
        hint = this.state.data.hint;
        selected = this.state.data.selected;

        if(Functions.isNull(value))
            hint = null;

        var className = "search-company-input";
        var from = this.props.from;
        if(from == 'comps'){
            className = "input-modal-full";
        }

        return (
            <div className="search" role="search">
                <input type="text"
                       className={className}
                       placeholder="通过产品名/公司名查找"
                       tabIndex="1"
                       autoCapitalize="off"
                       value={value}
                       onClick={this.click}
                       onChange={this.change}
                       onKeyDown={this.onKeyDown}/>

                <SearchHint data={hint} from={from}  selected={selected}/>

            </div>

        );
    },

    click(e){
        $('.search-company-hint').show();
        e.stopPropagation();

        //CompanyActions.get(companyName);
    },

    change(e){
        CompanyActions.change(e.target.value);
    },

    onKeyDown(e){

        if(Functions.isEmptyObject(this.state)){
            return;
        }else if(this.state.data.value == null){
            return;
        }


        CompanyActions.keydown(e.keyCode);
    }
});


const SearchHint = React.createClass({

    render() {
        var data = this.props.data;
        var selected = this.props.selected;

        if(Functions.isEmptyObject(data)){
            return null;
        }

        var companies = data.name;

        var className = 'search-company-hint ';
        if(this.props.from == 'comps')
            className += 'full-hint';

        return(
            <div className={className}>
                <div className="hint-type">
                    <ul>
                        {companies.map(function(result, index){
                            return  <HintElement key={index} data={result} selected={selected} />
                        })}

                    </ul>
                </div>
            </div>
        )

    }

});


const HintElement = React.createClass({
    render(){
        var className="hint-element ";
        var data = this.props.data;

        if(data == this.props.selected){
            className +="hint-selected";
        }

        return (
            <li className= {className}
                onMouseEnter={this.mouseOver}
                onMouseOut={this.mouseOut}
                onClick={this.click}>
                {data.name}
            </li>
        )

    },

    click(){
        CompanyActions.clickSearch();
    },

    mouseOver(){
        CompanyActions.select(this.props.data);
    },

    mouseOut(){
        CompanyActions.unselect();
    }


});



module.exports = CompanyInput;
