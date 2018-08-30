package com.tsb.user.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.user.CompanyListRel;

@SuppressWarnings("rawtypes")
public interface CompanyListRelReadDao {

	List<CompanyListRel> get(int id);

	List<CompanyListRel> getByCompanyId(int id);

	List getCompanyIds(int listId);

	CompanyListRel getCompanyListRel(@Param("companyListId") Integer companyListId,
			@Param("companyId") Integer companyId);
}
