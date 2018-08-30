package com.tsb.company.vo;

import com.tsb.model.org.user.DealNote;

public class DealNoteVO {

	private DealNote dealNote;
	private boolean owner;
	private String userName;

	public DealNote getDealNote() {
		return dealNote;
	}

	public void setDealNote(DealNote dealNote) {
		this.dealNote = dealNote;
	}

	public boolean isOwner() {
		return owner;
	}

	public void setOwner(boolean owner) {
		this.owner = owner;
	}

	public String getUserName() {
		return userName;
	}

	public void setUserName(String userName) {
		this.userName = userName;
	}

}
