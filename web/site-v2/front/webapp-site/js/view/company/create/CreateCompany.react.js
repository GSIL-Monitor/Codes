var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var CreateCompanyStore = require('../../../store/CreateCompanyStore');
var CreateCompanyActions = require('../../../action/CreateCompanyActions');
var Functions = require('../../../../../react-kit/util/Functions');
var CreateCompanyUtil = require('../../../util/CreateCompanyUtil');
var ValidateActions = require('../../../action/validation/NewCompanyActions');
/**** component ***/
var Name = require('./form/company/Name.react');
var FullName = require('./form/company/FullName.react');
var AddProduct = require('./form/product/AddProduct.react');
var Brief = require('./form/company/Brief.react');
var Description = require('./form/company/Description.react');
var Founder = require('./form/member/Founder.react');
var Education = require('./form/member/Education.react');
var Work = require('./form/member/Work.react');
var Phone = require('./form/member/Phone.react');
var NewSector = require('./form/sector/NewSector.react');
var NewTag = require('./form/tag/NewTag.react');
var Location = require('./form/company/Location.react');
var EstablishDate = require('./form/company/EstablishDate.react');
var Round = require('./form/company/Round.react');
var Investment = require('./form/company/Investment.react');
var ShareRatio = require('./form/company/ShareRatio.react');
var PreMoney = require('./form/company/PreMoney.react');
var PostMoney = require('./form/company/PostMoney.react');
var TeamSize = require('./form/member/TeamSize.react');
var UploadBP = require('./form/file/UploadBP.react');
var Note = require('./form/note/Note.react');
var SourceSelect = require('./form/source/SourceSelect.react');


const CreateCompany = React.createClass({

    mixins: [Reflux.connect(CreateCompanyStore, 'data')],

    componentWillMount() {
        CreateCompanyActions.getInitData(this.props.coldcallId,this.props.demodayId);
    },
    componentWillReceiveProps(nextProps) {
        CreateCompanyActions.getInitData(nextProps.coldcallId, nextProps.demodayId);
    },

    render(){
        if (Functions.isEmptyObject(this.state)) return null;

        var company = this.state.data.company;
        var member = this.state.data.member;
        var productList = this.state.data.productList;
        var parentSectors = this.state.data.parentSectors;
        var parentSectorId = this.state.data.parentSectorId;
        var subSectors = this.state.data.subSectors;
        var subSectorId = this.state.data.subSectorId;
        var teamSize = this.state.data.teamSize;
        var files =this.state.data.files;
        var location= this.state.data.location;
        var year = this.state.data.year;
        var month = this.state.data.month;
        var source = this.state.data.source;
        var add='添加';
        if(this.state.data.add){
            add='创建中...'
        }
        //<a className="a-red m-t-10 m-l-10 left" onClick={this.handleClean}>清除</a>

        return (
            <div className="main-create-company">
                <div className="create-company-title">新建公司</div>
                <Name data={company.name} onChange={this.onChange} id="companyName"/>
                <FullName data={company.fullName} onChange={this.onChange} id="fullName"/>
                <AddProduct data={productList} id="product"/>
                <NewSector parentSectors={parentSectors} subSectors={subSectors}
                           parentSectorId={parentSectorId} subSectorId={subSectorId} id="sector"/>
                <NewTag />
                <Brief data={company.brief} onChange={this.onChange} id="brief"/>
                <Description data={company.description} onChange={this.onChange}/>
                <Location data={location} id="locationId"/>
                <EstablishDate year={year} month={month} onChange={this.onChange}/>
                <Round data={company.round} onChange={this.onChange} id="round"/>
                <Investment data={company.investment} currency={company.currency} onChange={this.onChange} />
                <ShareRatio data={company.shareRatio} onChange={this.onChange} investment={company.investment}/>
                <PreMoney data={company.preMoney} onChange={this.onChange}/>
                <PostMoney data={company.postMoney} onChange={this.onChange}/>

                <TeamSize data={teamSize}  />
                <Founder data={member.name} onChange={this.onMemberChange} />
                <Education data={member.education} onChange={this.onMemberChange}/>
                <Work  data={member.work} onChange={this.onMemberChange}/>
                <Phone data={member.phone} onChange={this.onMemberChange}/>
                <UploadBP  data={files}  demodayId={this.props.demodayId}/>

                <Note onChange={this.onNoteChange}/>

                <SourceSelect  data={source}/>
                <button className="btn btn-navy btn-create-company" onClick={this.handleAdd}>{add}</button>
            </div>
        )
    },

    onChange(e){
        CreateCompanyActions.change(e.target.name, e.target.value);
    },
    onMemberChange(e){
        CreateCompanyActions.memberChange(e.target.name, e.target.value);
    },
    onNoteChange(e){
        CreateCompanyActions.changeNote(e.target.value);
    },
    handleAdd(){
        var company = this.state.data.company;
        var productList = CreateCompanyUtil.getProductList(this.state.data.productList);
        var parentSectorId = this.state.data.parentSectorId;
        var files =this.state.data.files;
        var source = this.state.data.source;
        var checkedAdd =true;
        var focused=false;

        if(this.state.data.add){
            checkedAdd=false;
        }
        if(company.name.trim()==''){
            ValidateActions.name(company.name);
            checkedAdd=false;
            if(!focused){
                $("#companyName").focus();
                focused=true;
            }
        }
        if(productList==null||productList.length==0){
            ValidateActions.product(productList);
            checkedAdd=false;
            if(!focused){
             $("#product").focus();
             focused=true;
            }
        }
        if(parentSectorId==null||parentSectorId==-1){
            ValidateActions.sector(parentSectorId);
            if(!focused ){
                $("#sector").focus();
                focused=true;
            }
            checkedAdd=false;
        }
         if(company.brief.trim()==''){
            ValidateActions.brief(company.brief);
             checkedAdd=false;
            if(!focused ){
                $("#brief").focus();
                focused=true;
            }

        }
        if(null==company.locationId||!Number(company.locationId)){
            ValidateActions.locationId(company.locationId);
            checkedAdd=false;
            if(!focused ){
                $("#locationId").focus();
                focused=true;
            }
        }
         if (company.round.trim()==''){
            ValidateActions.round(company.round);
            checkedAdd=false;
             if(!focused ){
                 $("#round").focus();
                 focused=true;
             }
        }
        if(this.props.demodayId){
            if(files.length==0){
                ValidateActions.uploadBp(files.length);
                checkedAdd=false;
            }

        }

        if(checkedAdd &&!this.state.data.add){
            CreateCompanyActions.add();
        }
    }
});

module.exports = CreateCompany;