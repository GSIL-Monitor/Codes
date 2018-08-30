package com.tsb.admin.service;

import java.util.List;

import com.tsb.admin.vo.MemberVO;
import com.tsb.admin.vo.SourceMemberVO;
import com.tsb.model.CompanyMemberRel;
import com.tsb.model.Member;

public interface MemberService {
	List<MemberVO> listMemberVOsByCompanyId(Integer id);
	List<SourceMemberVO> listSourceMemberVOsByCompanyMemberRelId(Integer id);
	void updateMemberAndRel(MemberVO memberVO);
	void deleteCompanyMemberRel(CompanyMemberRel companyMemberRel);
	void addMember(Member m);
	void updateMember(Member m);
	void deleteMember(Integer id);
}
