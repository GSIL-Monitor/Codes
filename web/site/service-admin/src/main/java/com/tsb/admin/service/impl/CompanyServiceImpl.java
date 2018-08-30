package com.tsb.admin.service.impl;

import java.sql.Timestamp;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.admin.dao.read.CompanyReadDao;
import com.tsb.admin.dao.read.LocationReadDao;
import com.tsb.admin.dao.read.source.SourceCompanyReadDao;
import com.tsb.admin.dao.write.CompanyWriteDao;
import com.tsb.admin.service.CompanyService;
import com.tsb.admin.vo.CompanyVO;
import com.tsb.model.Company;
import com.tsb.model.Funding;
import com.tsb.model.source.SourceCompany;

@Service
public class CompanyServiceImpl implements CompanyService{

	@Autowired
	private CompanyReadDao companyReadDao;
	
	@Autowired
	private CompanyWriteDao companyWriteDao;
	
	@Autowired
	private SourceCompanyReadDao sourceCompanyReadDao;
	
	@Autowired
	private LocationReadDao locationReadDao;
	
	@Override
	public Company get(Integer id) {
		return companyReadDao.getById(id);
	}

	@Override
	public Company get(String code) {
		return companyReadDao.getByCode(code);
	}

	@Override
	public void update(Company company) {
		Timestamp time = new Timestamp(System.currentTimeMillis());	
		
		company.setModifyTime(time);
		company.setModifyUser(0);
		company.setVerify('Y');
		
		companyWriteDao.update(company);
	}

	@Override
	public List<SourceCompany> getSource(Integer companyId) {
		return sourceCompanyReadDao.getByCompanyId(companyId);
	}

	@Override
	public Integer getLocation(String name) {
		Integer id =  locationReadDao.getByName(name);
		if(id == null)
			id = 0;
			
		return id;
	}

	@Override
	public void updateFunding(Funding funding) {
		Company company = companyReadDao.getById(funding.getCompanyId());
		if(funding.getRound() > company.getRound()){
			Timestamp time = new Timestamp(System.currentTimeMillis());	
			company.setRound(funding.getRound());
			company.setRoundDesc(funding.getRoundDesc());
			company.setPreMoney(funding.getPreMoney());
			company.setCurrency(funding.getCurrency());
			company.setFundingType(funding.getFundingType());
			company.setModifyTime(time);
			company.setModifyUser(0);
			company.setVerify('Y');
			companyWriteDao.update(company);
		}
		
	}

	@Override
	public List<CompanyVO> getCompaniesByIds(List companyIds) {
		return companyReadDao.getCompaniesByIds(companyIds);
	}
	
}
