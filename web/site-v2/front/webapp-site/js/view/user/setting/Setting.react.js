var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var SettingStore = require('../../../store/user/SettingStore');
var SettingActions = require('../../../action/user/SettingActions');
var SelectSector = require('./SelectSector.react');
var UserUtil = require('../../../util/UserUtil');
var Functions = require('../../../../../react-kit/util/Functions');
var FormInput = require('../../../../../react-kit/form/FormInput.react');

const Setting = React.createClass({

    mixins: [Reflux.connect(SettingStore, 'data')],

    componentWillMount(){
        SettingActions.init();
    },

    render(){
        var state = this.state;
        if (Functions.isEmptyObject(state))
            return null;

        var data = state.data;
        Functions.updateTitle('setting');

        var sectors = data.selectedSectors;
        var oldSectors = data.oldSectors;
        var recommendNum = data.recommendNum;
        var oldRecommendNum = data.oldRecommendNum;
        var comfirmBtn;
        if( UserUtil.isSame(sectors, oldSectors) &&
            oldRecommendNum == recommendNum){
            comfirmBtn = <button className="btn btn-gray btn-sector-comfirm disabled"> 确定 </button>
        }else{
            comfirmBtn = <button className="btn btn-navy btn-sector-comfirm" onClick={this.comfirmClick}> 确定 </button>
        }

        return(
            <div>
                <SelectSector data={data}/>
                <div className="all-block">
                    <h2>基本设置</h2>

                    <div className="setting-form-part">
                        <label>
                            <span>系统分配数量</span>
                        </label>
                        <input type="text"
                               name="recommendNum"
                               value={data.recommendNum}
                               onChange={this.change}
                               placeholder= '默认为2, 修改范围 2~99'
                            />
                    </div>

                    <div className="sector-comfirm">
                        {comfirmBtn}
                     </div>

                </div>
            </div>
        )
    },

    change(e){
        SettingActions.changeRecommendNum(e.target.value);
    },

    comfirmClick(){
        SettingActions.update();
    }
});


module.exports = Setting;