package com.tsb.model.vo;

import com.tsb.model.CompanyMemberRel;
import com.tsb.model.Member;

public class CompanyMemberRelVO {

	private CompanyMemberRel companyMemberRel;
	private Member member;

	public CompanyMemberRel getCompanyMemberRel() {
		return companyMemberRel;
	}

	public void setCompanyMemberRel(CompanyMemberRel companyMemberRel) {
		this.companyMemberRel = companyMemberRel;
	}

	public Member getMember() {
		return member;
	}

	public void setMember(Member member) {
		this.member = member;
	}

}
