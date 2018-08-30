var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var LocationStore = require('../../store/SearchLocationStore');
var LocationActions = require('../../action/SearchLocationActions');

var Functions = require('../../util/Functions');

var LocationInput = React.createClass({
    mixins: [Reflux.connect(LocationStore, 'data')],

    componentWillMount() {
        LocationActions.init(this.props.value, this.props.id, this.props.from);
    },

    componentWillReceiveProps(nextProps) {
        LocationActions.init(nextProps.value, nextProps.id, nextProps.from);
    },

    render() {
        var hint = null;
        var selected = null;
        var placeholder = this.props.placeholder;
        if(Functions.isNull(placeholder)){
            placeholder = '地点';
        }

        if(Functions.isEmptyObject(this.state)){
            return (
                <div className="search search-location" role="search">
                    <input type="text" className="search-location-input" placeholder={placeholder} />
                </div>
            )
        }

        var location = this.state.data.location;
        hint = this.state.data.hint;
        selected = this.state.data.selected;

        if(Functions.isNull(location))
            hint = null;

        var from = this.props.from;

        return (
            <div className="search search-location" role="search">
                <input type="text"
                       className={this.props.className}
                       placeholder={placeholder}
                       tabIndex="1"
                       autoCapitalize="off"
                       value={location}
                       onClick={this.click}
                       onChange={this.change}
                       onKeyDown={this.onKeyDown}
                       onBlur={this.blur}
                       id={this.props.id}
                    />

                <SearchHint data={hint} selected={selected} from={from}/>

            </div>

        );
    },

    click(e){
        $('.search-location-hint').show();
        e.stopPropagation();

    },

    change(e){
        LocationActions.change(e.target.value);
    },

    onKeyDown(e){

        if(Functions.isEmptyObject(this.state)){
            return;
        }else if(this.state.data.location == null){
            return;
        }

        LocationActions.keydown(e.keyCode);
    },

    blur(e){
        LocationActions.validateLocation();
    }
});


const SearchHint = React.createClass({

    render() {
        var data = this.props.data;
        var selected = this.props.selected;


        if(Functions.isEmptyObject(data)){
            return null;
        }

        var className = 'search-location-hint ';
        var from = this.props.from;
        if(from == 'createCompany'){
            className += 'search-location-hint-short';
        }else if(from == 'newCollection'){
            className += 'search-collection-location-hint';
        }




        var hints = data.location;

        return(
            <div className={className}>
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
        LocationActions.clickSearch();
    },

    mouseOver(){
        LocationActions.select(this.props.data);
    }


});



module.exports = LocationInput;
