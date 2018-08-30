package com.tsb.company.service.impl;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.service.CompanyService;
import com.tsb.company.service.RecommendationService;
import com.tsb.company.vo.CompanySearchVO;
import com.tsb.company.vo.CompanyVO;
import com.tsb.dao.read.user.RecommendationReadDao;
import com.tsb.model.user.Recommendation;

@Service
public class RecommendationServiceImpl implements RecommendationService{

	@Autowired
	private RecommendationReadDao rReadDao;
	
	@Autowired
	private CompanyService companyService;
	
	@Override
	public List<CompanySearchVO> get(Integer userId) {
		List<Recommendation> recommendations =  rReadDao.get(userId);
		List<Integer> ids = new ArrayList<Integer>();
		if(recommendations.size() == 0) 
			return null;
		
		for(Recommendation re: recommendations){
			ids.add(re.getCompanyId());
		}
		
		return companyService.getCompaniesByIds(ids);
	}
}
