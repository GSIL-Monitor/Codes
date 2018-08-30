package com.tsb.admin.vo;

import com.tsb.model.source.SourceCompanyMemberRel;
import com.tsb.model.source.SourceMember;

public class SourceMemberVO {
	private SourceCompanyMemberRel rel;
	private SourceMember	member;
	
	//*******************************
	public SourceCompanyMemberRel getRel() {
		return rel;
	}
	public void setRel(SourceCompanyMemberRel rel) {
		this.rel = rel;
	}
	public SourceMember getMember() {
		return member;
	}
	public void setMember(SourceMember member) {
		this.member = member;
	}
}
