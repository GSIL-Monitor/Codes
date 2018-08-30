package com.tsb.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.Company;
import com.tsb.model.CompanyMemberRel;
import com.tsb.model.vo.CompanyHeadVO;
import com.tsb.model.vo.CompanyVO;
import com.tsb.model.vo.FollowCompany;

@SuppressWarnings("rawtypes")
public interface CompanyReadDao {

	Integer getIdByCode(String code);

	List getIdsByCodes(@Param("codeList") List codes);

	CompanyVO getCompanyVO(Integer companyId);

	Company get(String code);

	List<Company> getCompanies(@Param("codes") List codes);

	List<FollowCompany> getFollowCompanies(@Param("userId") int userId, @Param("companyIds") List companyIds);

	List<CompanyMemberRel> getComMemRelById(Integer companyId);
	
	CompanyHeadVO getCompanyHeadVO(Integer companyId);
	//test
	FollowCompany getFollowCompany(@Param("userId") int userId, @Param("companyId") int companyId);
}
