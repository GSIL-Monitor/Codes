var React = require('react');
var ReactDom = require('react-dom');
var Reflux = require('reflux');
var $ = require('jquery');

var SearchStore = require('../../store/SearchStore');
var SearchActions = require('../../action/SearchActions');
var HeaderActions = require('../../action/HeaderActions');

var Functions = require('../../util/Functions');

var searchValue;


var MobileSearchBar = React.createClass({
    mixins: [Reflux.connect(SearchStore, 'data')],

    componentWillMount() {
        SearchActions.initMobile(this.props.value);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.value == nextProps.value) return;
        SearchActions.initMobile(nextProps.value);
    },

    componentDidMount(){
        //if(ReactDom.findDOMNode(this.refs.search) != null){
        //    ReactDom.findDOMNode(this.refs.search).focus();
        //}
    },

    render() {
        var hint = null;
        var selected = null;

        var data= this.state.data;
        if(!Functions.isNull(data)){
            searchValue = data.search;
            hint = data.hint;
            selected = data.selected;
        }

        var classname= this.props.className;
        if(classname== null){
            classname ="m-search-input";
        }

        return (
            <div role="search">
                <input type="text"
                       className={classname}
                       placeholder="Search"
                       ref="search"
                       tabIndex="1"
                       autoCapitalize="off"
                       value={searchValue}
                       onClick={this.click}
                       onChange={this.change}
                       onKeyDown={this.onKeyDown}
                    />

                <button className="search-icon" onClick={this.clickSearch}>
                    <i className="fa fa-search fa-xl"></i>
                </button>

                <SearchHint data={hint} selected={selected}/>

            </div>

        );
    },

    click(e){
        $('.search-hint').show();
        e.stopPropagation();

        SearchActions.get(searchValue);
    },

    change(e){
        SearchActions.change(e.target.value);
    },

    clickSearch(){
        SearchActions.clickSearch();
    },

    onKeyDown(e){
        SearchActions.keydown(e.keyCode);
        if(e.keyCode == 13){
            //$('.page-wrapper, .search-main, footer').show();
            $('.search-icon').focus();
            HeaderActions.clickSearchClose();
        }
    }

});


const SearchHint = React.createClass({

    render() {
        var companies = null;
        var keywords = null;

        var data = this.props.data;
        var selected = this.props.selected;

        if(data == null){
            return null;
        }else{
            for(var k in data){
                if(k == 'name'){
                    companies = data[k];
                }else if(k == 'keyword'){
                    keywords = data[k];
                }
            }
        }

        var hint_close;
        if(companies.length > 0 || keywords.length > 0){
            hint_close = <a className="hint-close" onClick={this.close}>关闭</a>
        }


        return(
            <div className="search-hint">
                {hint_close}
                <HintType data={companies} name="公司" selected={selected}/>
                <HintType data={keywords} name="标签" selected={selected}/>
            </div>
        )
    },

    close(){
        $('.hint-close').focus();
        $('.search-hint').hide();
    }

});


const HintType = React.createClass({
    render(){
        var name = this.props.name;
        var data = this.props.data;
        var selected = this.props.selected;

        if(data == null){
            return null;
        }

        return(
            <div className="hint-type">
                <div className="search-divider" onClick={this.click}>
                    {name}
                </div>

                <ul>
                    {data.map(function(result, index){
                            return  <HintElement key={index}
                                                 name={name}
                                                 data={result}
                                                 selected={selected} />
                    })}
                </ul>
            </div>
        )
    },

    click(e){
        $('.search-hint').show();
        e.stopPropagation();
    }

});

const HintElement = React.createClass({
    render(){
        var className="hint-element ";
        var type = this.props.name;
        var name;
        var completion;
        var show;
        var data = this.props.data;

        if(data == this.props.selected){
            className +="hint-selected";
        }


        for(var k in data){
            if(k == 'name'){
                name = data[k]
            }
            if( k == 'completion'){
                completion = data[k]
            }
        }

        if( name != null){

            show = name + ' -- '+ completion;
        }else{
            show = completion;
        }

        show = name;

        return (
            <li className= {className}
                onMouseEnter={this.mouseOver}
                onMouseOut={this.mouseOut}
                onClick={this.click}>
                {show}
            </li>
        )

    },

    click(){
        SearchActions.clickSearch();
    },

    mouseOver(){
        SearchActions.select(this.props.data);
    },

    mouseOut(){
        SearchActions.unselect();
    }

});


module.exports = MobileSearchBar;
