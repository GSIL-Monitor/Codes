package com.tsb.service;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.Artifact;
import com.tsb.model.Company;
import com.tsb.model.Member;
import com.tsb.model.vo.CompanyHeadVO;
import com.tsb.model.vo.CompanyMemberRelVO;
import com.tsb.model.vo.CompanyVO;
import com.tsb.model.vo.FollowCompany;
import com.tsb.model.vo.MemberExperience;

@SuppressWarnings("rawtypes")
public interface CompanyService {
	Company get(String code);

	Integer getIdByCode(String code);

	CompanyVO getByCode(String code);

	List<FollowCompany> getFollowCompanies(int userId, @Param("companyIdS") List companyIds);

	List getIdsByCompanyCodes(List<String> companyCodes);

	List<CompanyVO> getCompanies(List compIdList);

	List<CompanyMemberRelVO> getMembers(Integer companyId);

	CompanyHeadVO getHeadInfo(Integer userId, Integer companyId);

	Member getMember(int id);

	List<MemberExperience> getMemberExperienc(int memberId);

	List<Artifact> getArtifacts(int companyId, int artifactType);

	void verify(int companyId, Character verify);
}
