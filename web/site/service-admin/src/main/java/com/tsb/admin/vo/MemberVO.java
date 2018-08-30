package com.tsb.admin.vo;

import com.tsb.model.CompanyMemberRel;
import com.tsb.model.Member;

public class MemberVO {
	private CompanyMemberRel rel;
	private Member	member;
	
	//*******************************
	public CompanyMemberRel getRel() {
		return rel;
	}
	public void setRel(CompanyMemberRel rel) {
		this.rel = rel;
	}
	public Member getMember() {
		return member;
	}
	public void setMember(Member member) {
		this.member = member;
	}
}
