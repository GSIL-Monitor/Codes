var React = require('react');
var Reflux = require('reflux');
var $ = require('jquery');

var Functions = require('../../../../../../../react-kit/util/Functions');
var FormInput = require('../FormInput.react');
var CompanyUtil = require('../../../../../util/CompanyUtil');
var FormSelect = require('../FormSelect.react');

const EstablishDate = React.createClass({

    render(){


        var year =  this.props.year;
        var month =  this.props.month;

        var yearSelect = CompanyUtil.yearSelect();
        var monthSelect = CompanyUtil.monthSelect();

        var yearClass = 'input-update-small ';
        var monthClass = 'input-update-small ';

        return (
            <div className="create-company-form" >
                <div className='cc-form-left'>
                    <span>成立时间</span>
                </div>
                <div className="cc-form-right">
                    <div className="form-input">
                        <FormSelect className={yearClass}
                                      name='year'
                                      value={year}
                                      select={yearSelect}
                            />

                        <FormSelect className={monthClass}
                                      name='month'
                                      value={month}
                                      select={monthSelect}
                            />
                    </div>
                </div>
            </div>
        )

    }
});


module.exports = EstablishDate;