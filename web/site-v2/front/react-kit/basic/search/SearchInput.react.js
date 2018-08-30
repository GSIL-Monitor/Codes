var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SearchStore = require('../../store/SearchStore');
var SearchActions = require('../../action/SearchActions');

var Functions = require('../../util/Functions');

var SearchBar = React.createClass({
    mixins: [Reflux.connect(SearchStore, 'data')],

    componentWillMount() {
        SearchActions.init(this.props.type, this.props.value);
    },

    componentWillReceiveProps(nextProps) {
        if(this.props.type == nextProps.type && this.props.value == nextProps.value) return;
        SearchActions.init(nextProps.type, nextProps.value);
    },

    render() {
        var className= this.props.className;
        var icon = this.props.icon;

        if(Functions.isEmptyObject(this.state)){
            return <SearchBody className={className} />
        }

        var data = this.state.data;

        var value = data.search;
        var hint = data.hint;
        var selected = data.selected;

        if(Functions.isNull(value))
            hint = null;


        return <SearchBody className={className} value={value} hint={hint} selected={selected} icon={icon}/>
    }

});


const SearchBody = React.createClass({

    render(){
        var icon;
        if(this.props.icon){
            icon = <button className="search-icon" onClick={this.clickSearch}>
                        <i className="fa fa-search fa-xl"></i>
                    </button>
        }

        return(
            <div className="search left" role="search">
                <input type="text"
                       className={this.props.className}
                       placeholder="Search"
                       ref="search"
                       tabIndex="1"
                       autoCapitalize="off"
                       value={this.props.value}
                       onClick={this.click}
                       onChange={this.change}
                       onKeyDown={this.onKeyDown}/>

                {icon}

                <SearchHint data={this.props.hint} selected={this.props.selected}/>

            </div>
        )
    },

    click(e){
        $('.search-hint').show();
        e.stopPropagation();

        SearchActions.get(this.props.value);
    },

    change(e){
        SearchActions.change(e.target.value);
    },

    clickSearch(){
        SearchActions.clickSearch();
    },

    onKeyDown(e){
        if(e.keyCode === 38 || e.keyCode === 40){
            $('.search-input').select();
        }

        SearchActions.keydown(e.keyCode);
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

        return(
            <div className="search-hint">
                <HintType data={companies} name="公司" selected={selected}/>
                <HintType data={keywords} name="标签" selected={selected}/>

            </div>
        )


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

        //if(type == '标签'){
            show = name;
        //}

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



module.exports = SearchBar;
