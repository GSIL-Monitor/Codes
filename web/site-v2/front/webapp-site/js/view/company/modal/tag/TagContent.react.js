var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CompanyStore = require('../../../../store/CompanyStore');
var CompanyActions = require('../../../../action/CompanyActions');
var Functions = require('../../../../../../react-kit/util/Functions');
var TagInput = require('../../../../../../react-kit/basic/search/TagInput.react');
var AddTagList = require('./AddTagList.react');
var CreateCompanyStore = require('../../../../store/CreateCompanyStore');
var CreateCompanyActions = require('../../../../action/CreateCompanyActions');

const TagContent = React.createClass({

    mixins: [Reflux.connect(CompanyStore, 'data'),
        Reflux.connect(CreateCompanyStore, 'ccData')
        ],

    render(){

        //<button className="btn btn-navy btn-modal-comfirm" onClick={this.add}>
        //    {this.props.name}
        //</button>
        var state= this.state;
        if(Functions.isEmptyObject(state))
            return null;

        var from = this.props.from;
        if(from == null){
            from = 'updateCompany';
        }

        var newTags;
        if(state.data!=null){
            newTags = state.data.newTags;
            return(
                <div>
                    <div className="tag-list">
                        <AddTagList data={newTags} />
                    </div>

                    <TagInput  className="input-modal-full"  from={from}/>

                </div>
            )
        }
        if(state.ccData!=null){
            newTags = state.ccData.newTags;
            return(
                <div>

                    <div className="cc-tag-list">
                        <AddTagList data={newTags} from="createCompany"/>
                    </div>
                    <TagInput  className="input-modal-short"  from="createCompany"/>
                </div>
            )
        }
    },

    add(e){
        CompanyActions.addTag(e.target.value);
    }
});


module.exports = TagContent;