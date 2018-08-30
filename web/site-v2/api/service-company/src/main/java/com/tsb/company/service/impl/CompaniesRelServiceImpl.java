package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.dao.CompanyVODao;
import com.tsb.company.service.CompaniesRelService;
import com.tsb.company.service.CompanyService;
import com.tsb.company.service.FundingService;
import com.tsb.company.service.SectorService;
import com.tsb.company.service.TagService;
import com.tsb.company.vo.CompsVO;
import com.tsb.dao.read.LocationReadDao;
import com.tsb.dao.read.company.CompaniesRelReadDao;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.write.company.CompaniesRelWriteDao;
import com.tsb.model.company.CompaniesRel;
import com.tsb.model.company.Company;
import com.tsb.model.company.Sector;

@Service
@SuppressWarnings("rawtypes")
public class CompaniesRelServiceImpl implements CompaniesRelService{

	@Autowired
	private CompaniesRelReadDao crReadDao;
	
	@Autowired
	private CompanyVODao companyVODao;
	
	@Autowired
	private CompanyReadDao companyReadDao;
	
	@Autowired
	private LocationReadDao locationReadDao;
	
	@Autowired
	private FundingService fundingService;
	
	@Autowired
	private CompaniesRelWriteDao crWriteDao;
	
	@Autowired
	private TagService tagService;
	
	@Autowired
	private SectorService sectorService;
	
	@Autowired
	private CompanyService companyService;
	
	@Override
	public CompsVO getByCode(String code) {
		
		CompsVO compsVO = new CompsVO();
		Company company = companyReadDao.getByCode(code);
		compsVO.setCompany(company);
		compsVO.setLocation(locationReadDao.get(company.getLocationId()));
		compsVO.setTags(tagService.getTags(company.getId()));
		compsVO.setFundings(fundingService.get(company.getId()));
		compsVO.setSectors(sectorService.getByCompanyId(company.getId()));
			
		return compsVO;
	}
	
	
	@Override
	public List get(Integer companyId) {
		List<CompaniesRel> rels = crReadDao.get(companyId);
//		List<CompsVO> result = new ArrayList<CompsVO>();
//		for(CompaniesRel rel : rels){
//			Integer id = rel.getCompany2Id();
//			CompsVO compsVO = new CompsVO();
//			Company company = companyReadDao.getById(id);
//			compsVO.setCompany(company);
//			compsVO.setLocation(locationReadDao.get(company.getLocationId()));
//			compsVO.setTags(tagService.getTags(id));
//			compsVO.setFundings(fundingService.get(id));
//			compsVO.setSectors(sectorService.getByCompanyId(id));
//			
//			result.add(compsVO);
//		}
//		return result;
		
		List companyIds = new ArrayList();
		if(rels.size() == 0) return companyIds;
		
		for(CompaniesRel cr : rels){
			companyIds.add(cr.getCompany2Id());
		}
		return companyService.getCompaniesByIds(companyIds);
		

	}

	@Override
	public void add(List<Integer> ids, Integer companyId, Integer userId) {
		for(Integer id : ids){
			CompaniesRel cr = new CompaniesRel();
			Timestamp time = new Timestamp(System.currentTimeMillis());
			cr.setCompany2Id(id);
			cr.setCompanyId(companyId);
			cr.setCreateTime(time);
			cr.setCreateUser(userId);
			cr.setActive('Y');
			cr.setVerify('Y');
			crWriteDao.insert(cr);
		}
	}

	@Override
	public void delete(List<Integer> ids, Integer companyId, Integer userId) {
		for(Integer id : ids){
			CompaniesRel cr = new CompaniesRel();
			Timestamp time = new Timestamp(System.currentTimeMillis());
			cr.setCompany2Id(id);
			cr.setCompanyId(companyId);
			cr.setModifyTime(time);
			cr.setModifyUser(userId);
			cr.setActive('N');
			cr.setVerify('N');
			crWriteDao.delete(cr);
		}		
	}

	

}
