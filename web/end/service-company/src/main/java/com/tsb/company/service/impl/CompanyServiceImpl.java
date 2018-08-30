package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.dao.CompanyVODao;
import com.tsb.company.service.CompanyService;
import com.tsb.company.vo.CompanySearchVO;
import com.tsb.company.vo.CompanyVO;
import com.tsb.dao.read.CompanyReadDao;
import com.tsb.dao.read.LocationReadDao;
import com.tsb.dao.read.source.SourceCompanyReadDao;
import com.tsb.dao.write.CompanyWriteDao;
import com.tsb.model.Company;
import com.tsb.model.Funding;
import com.tsb.model.source.SourceCompany;

@Service
public class CompanyServiceImpl implements CompanyService{

	@Autowired
	private CompanyVODao companyVODao;
	
	@Override
	public CompanyVO get(String code) {
		return companyVODao.getByCode(code);
	}

	@Override
	public List<CompanySearchVO> getCompaniesByIds(List companyIds) {
		return companyVODao.getSearch(companyIds);
	}
	
	
}
