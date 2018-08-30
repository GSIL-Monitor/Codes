var React = require('react');
var ReactDom = require('react-dom');
var Reflux = require('reflux');
var $ = require('jquery');

var UserCompanyStore = require('../../../store/UserCompanyStore');
var UserCompanyActions = require('../../../action/UserCompanyActions');
var Functions = require('../../../../../react-kit/util/Functions');
var NoteUtil = require('../../../util/NoteUtil');

const Note = React.createClass({

    render(){

        var me = this;
        var notes = this.props.notes;

        var noteList;
        var noteSum;
        if (notes != null) {
            if (notes.length > 6) {
                noteNav = <div className="i-more">
                    <i className="fa fa-angle-double-down"></i>
                </div>
            }

            if (notes.length > 0) {
                noteList = <div className="note-list" onMouseOver={this.onMouseOver} onMouseOut={this.onMouseOut}>
                    {notes.map(function (result, index) {
                        return <NoteItem key={index}
                                         data={result}
                                         updateNote={me.updateNote}
                                         deleteNote={me.deleteNote}/>
                    })}
                </div>;

                noteSum = <span className="note-sum"></span>;
            }

        }
        return (
            <div>
                <div className="user-mark user-note m-t-5" onClick={this.noteClick}>
                    <span>笔记</span>
                    {noteSum}
                </div>

                <div className="div-note">
                    {noteList}
                 <textarea className="add-note-textarea"
                           name='noteText'
                           ref='note'
                           value={this.props.noteText}
                           onChange={this.handleChange}
                           onClick={this.noteClick}/>
                    <a className="add-note" onClick={this.addNote}>提交</a>
                </div>
            </div>

        )
    },

    handleChange(event){
        UserCompanyActions.change(event.target.name, event.target.value);
    },

    addNote(e){
        var note = this.props.noteText;
        if (note != null && note != '') {
            UserCompanyActions.note(note);
        }
        $('.div-note').show();
        $('.user-mark1, .user-coldcall').hide();
        e.stopPropagation();
    },

    updateNote(note, noteId){
        UserCompanyActions.note(note, noteId);
    },

    deleteNote(noteId){
        UserCompanyActions.delete(noteId);
    },


    noteClick(e){
        $('.div-note').show();
        $('.user-mark1, .user-coldcall').hide();
        e.stopPropagation();
        ReactDom.findDOMNode(this.refs.note).focus();
    }
});

const NoteItem = React.createClass({

    getInitialState(){
        return {selected: false, update: false}
    },

    render(){
        var item = this.props.data;
        var note = item.dealNote.note;
        if(note == null) return null;
        var owner = item.owner;
        if (this.state.update) {
            return (
                <div className="note-item update-note-item" onClick={this.stopHide}>
                    <textarea className="update-note-textarea" ref='dealNote'
                              defaultValue={note}
                        />

                    <div className="text-right  m-t-5">
                        <a className="left" onClick={this.deleteNote}>
                            <i className="fa fa-times text-red"></i>
                        </a>
                        <a className="soft-text m-r-10" onClick={this.updateNote}>确认修改</a>
                        <a className="soft-text" onClick={this.cancel}>取消</a>
                    </div>
                </div>
            )
        }


        var createTime = item.dealNote.createTime;
        createTime = NoteUtil.parseTimestamp(createTime);

        if (!this.state.selected) {
            if (note.length > 100) {
                note = note.substring(0, 100) + '...';
            }
        }


        var update;
        if (owner) {
            update = <a className="a-button right m-r-5" onClick={this.updateItem}>修改</a>
        }

        return (
            <div className="note-item" onClick={this.stopHide}>
                <div onClick={this.click}>{note}</div>
                <div className="note-user">
                    {item.userName}
                    <span className="note-date">{createTime} </span>
                    {update}
                </div>

            </div>
        )
    },

    stopHide(e){
        $('.div-note').show();
        $('.user-mark1, .user-coldcall').hide();
        e.stopPropagation();
    },

    updateItem(e){
        this.setState({update: true});
    },

    click(e){
        if (this.state.selected)
            this.setState({selected: false});
        else {
            this.setState({selected: true});
        }

    },

    updateNote(e){
        var noteId = this.props.data.dealNote.id;
        var note = this.refs.dealNote.value;
        this.props.updateNote(note, noteId);
        this.cancel();

    },
    deleteNote(){
        this.props.deleteNote(this.props.data.dealNote.id);
        this.cancel();
    },

    cancel(e){
        this.setState({update: false});
    }
});
module.exports = Note;