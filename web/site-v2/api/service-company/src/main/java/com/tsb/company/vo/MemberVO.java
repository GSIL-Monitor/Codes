package com.tsb.company.vo;

import com.tsb.model.company.CompanyMemberRel;
import com.tsb.model.company.Member;

public class MemberVO {

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
