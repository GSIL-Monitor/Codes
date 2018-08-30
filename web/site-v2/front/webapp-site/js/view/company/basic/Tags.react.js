var React = require('react');
var Functions = require('../../../../../react-kit/util/Functions');
var CompanyActions = require('../../../action/CompanyActions');
var TagInput = require('../../../../../react-kit/basic/search/TagInput.react');


const Tags = React.createClass({
    render(){
        var data = this.props.data;
        var tags;
        if(data != null){
            if(data.length > 0){
                tags = data.map(function (result, index) {
                    return <TagItem key={index} data={result}/>;
                })
            }
        }

        return(
            <div className="section-sub-item last-sub-item">
                <div className="section-sub-item-name">标签：</div>
                <div className="section-sub-item-content">
                    {tags}
                    <TagInput from="company" />

                </div>
            </div>
        )
    }

});

const TagItem = React.createClass({

    getInitialState: function() {
        return {selected: false};
    },

    render(){
        var change;
        if(this.state.selected)
            change = true;

        if(change){
            return <span className="label tag"
                         onMouseEnter={this.onMouseEnter}
                         onMouseLeave={this.onMouseLeave}
                         onClick={this.click}>
                       {this.props.data.name}
                        <span className="delete-icon" onClick={this.deleteTag}>
                            <i className="fa fa-times fa-lg"></i>
                        </span>
                    </span>
        }


        return(
            <span className="label tag"
                  onMouseEnter={this.onMouseEnter}
                  onMouseLeave={this.onMouseLeave}
                  onClick={this.click}>
               {this.props.data.name}
            </span>
        )
    },

    onMouseEnter(){
        this.setState({selected: true})
    },

    onMouseLeave(){
        this.setState({selected: false})
    },

    click(){
        CompanyActions.searchTag(this.props.data.name);
        this.setState({selected: false});
    },

    deleteTag(){
        CompanyActions.deleteTagDB(this.props.data.id)
    }
});


module.exports = Tags;