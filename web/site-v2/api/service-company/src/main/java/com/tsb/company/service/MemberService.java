package com.tsb.company.service;

import java.util.List;

import com.tsb.company.vo.MemberVO;
import com.tsb.model.company.Member;

public interface MemberService {
	List<MemberVO> getMembers(Integer companyId);
	void addCompanyMember(Member member,Integer companyId,Integer userId);
}
