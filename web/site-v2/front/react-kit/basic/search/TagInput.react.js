var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var TagStore = require('../../store/SearchTagStore');
var TagActions = require('../../action/SearchTagActions');

var Functions = require('../../util/Functions');

var TagInput = React.createClass({
    mixins: [Reflux.connect(TagStore, 'data')],

    componentWillMount() {
        TagActions.init(this.props.from);
    },

    componentWillReceiveProps(nextProps) {
        TagActions.init(nextProps.from);
    },

    render() {
        var className= this.props.className;
        var hint = null;
        var selected = null;

        if(Functions.isEmptyObject(this.state)){
            return null;
        }

        var value = this.state.data.tag;
        hint = this.state.data.hint;
        selected = this.state.data.selected;
        var placeholder = '标签名';

        if(Functions.isNull(value))
            hint = null;

        var from = this.props.from;
        if(from == 'company'){
            className = 'company-add-tag';
            placeholder = '添加标签';
        }


        return (
            <div className="search" role="search">
                <input type="text"
                       className={className}
                       placeholder={placeholder}
                       tabIndex="1"
                       autoCapitalize="off"
                       value={value}
                       onClick={this.click}
                       onChange={this.change}
                       onKeyDown={this.onKeyDown}/>

                <SearchHint data={hint} from={from} selected={selected}/>

            </div>

        );
    },

    click(e){
        $('.search-tag-hint').show();
        e.stopPropagation();

    },

    change(e){
        TagActions.change(e.target.value);
    },

    onKeyDown(e){

        if(Functions.isEmptyObject(this.state)){
            return;
        }else if(this.state.data.tag == null){
            return;
        }

        TagActions.keydown(e.keyCode);
    }
});


const SearchHint = React.createClass({

    render() {
        var data = this.props.data;
        var selected = this.props.selected;

        if(Functions.isEmptyObject(data)){
            return null;
        }

        var from = this.props.from;

        var className = 'search-tag-hint ';
        if(from == 'createCompany'){
            className += 'search-tag-hint-short';
        }else if(from == 'company'){
            className += 'search-company-add-tag-hint';
        }else if(from == 'newCollection'){
            className += 'search-collection-tag-hint';
        }


        var hints = data.keyword;

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
        TagActions.clickSearch();
    },

    mouseOver(){
        TagActions.select(this.props.data);
    }


});



module.exports = TagInput;
