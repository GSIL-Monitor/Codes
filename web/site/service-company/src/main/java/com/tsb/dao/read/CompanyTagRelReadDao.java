package com.tsb.dao.read;

import java.util.List;

import com.tsb.model.vo.CompanyTagRelVO;

public interface CompanyTagRelReadDao {
	List<CompanyTagRelVO> getByCompanyId(Integer companyId);
}
