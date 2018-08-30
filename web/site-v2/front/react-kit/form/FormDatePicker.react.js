var React = require('react');
var ReactPropTypes = React.PropTypes;

var DayPicker = require('react-day-picker');
var Moment = require('moment');

var $ = require('jquery');

var FormDatePicker = React.createClass({

    render: function() {
        if(this.props.value == null){
            return null
        }else{
            var date = Moment(this.props.value).format("L");
            var month = new Date(Date.parse(this.props.value));

            return (
                <div className="form-part">
                    <label>{this.props.label}</label>

                    <input
                        ref="input"
                        type="text"
                        value={date}
                        placeholder="YYYY-MM-DD"
                        onClick={this.handleClick}
                        onFocus={ this.showCurrentDate.bind(this) } />

                    <DayPicker
                        ref="daypicker"
                        initialMonth={month}
                        className="m-l-40 m-t-5 day-picker"
                        modifiers={{
                              }}
                        onDayClick={ this.handleDayClick.bind(this) }
                        />
                </div>
            );
        }
    },

    handleClick(e){
        $('.day-picker').css('display','flex');
        e.stopPropagation();


        $('.DayPicker').click(function(e){
            $('.day-picker').css('display', 'flex');
            e.stopPropagation();
        });
    },


    handleChange(e) {

    },

    handleDayClick(e, day) {
        this.setState({
            value: Moment(day).format("L"),
            month: day
        });
    },

    showCurrentDate() {
        this.refs.daypicker.showMonth(this.state.month);
    }




});

module.exports = FormDatePicker;
