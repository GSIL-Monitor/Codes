var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var InvestorStore = require('../../store/SearchInvestorStore');
var InvestorActions = require('../../action/SearchInvestorActions');

var Functions = require('../../util/Functions');

var InvestorInput = React.createClass({
    mixins: [Reflux.connect(InvestorStore, 'data')],

    componentWillMount() {
        InvestorActions.init(this.props.value, this.props.from);
    },

    componentWillReceiveProps(nextProps) {
        InvestorActions.init(nextProps.value, nextProps.from);
    },

    render() {
        var hint = null;
        var selected = null;

        if(Functions.isEmptyObject(this.state)){
            return <input type="text" className="search-investor-input" placeholder="投资机构/个人" />
        }

        var value = this.state.data.value;
        hint = this.state.data.hint;
        selected = this.state.data.selected;

        if(Functions.isNull(value))
            hint = null;

        return (
            <div className="search" role="search">
                <input type="text"
                       className={this.props.className}
                       placeholder="投资机构/个人"
                       tabIndex="1"
                       autoCapitalize="off"
                       value={value}
                       onClick={this.click}
                       onChange={this.change}
                       onKeyDown={this.onKeyDown}/>

                <SearchHint data={hint} selected={selected}/>
            </div>

        );
    },

    click(e){
        $('.search-investor-hint').show();
        e.stopPropagation();

    },

    change(e){
        InvestorActions.change(e.target.value);
    },

    onKeyDown(e){

        if(Functions.isEmptyObject(this.state)){
            return;
        }else if(this.state.data.value == null){
            return;
        }

        InvestorActions.keydown(e.keyCode);
    }
});


const SearchHint = React.createClass({

    render() {
        var data = this.props.data;
        var selected = this.props.selected;

        if(Functions.isEmptyObject(data)){
            return null;
        }

        var hints = data.investor;

        return(
            <div className="search-investor-hint">
                <div className="hint-type">
                    <ul>
                        {hints.map(function(result, index){
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
        InvestorActions.clickSearch();
    },

    mouseOver(){
        InvestorActions.select(this.props.data);
    }


});



module.exports = InvestorInput;
