package com.tsb.admin.service;

import java.util.List;

import com.tsb.admin.vo.AvgPreScoreVO;
import com.tsb.admin.vo.DemodayCompanyVO;
import com.tsb.admin.vo.DemodayDetailVO;
import com.tsb.admin.vo.DemodayOrgVO;
import com.tsb.admin.vo.UserPreScoreVO;
import com.tsb.model.demoday.Demoday;

@SuppressWarnings("rawtypes")
public interface DemodayService {
	
	List<UserPreScoreVO> getAllUserPreScore(Integer dealDemodayId);
	
	List<AvgPreScoreVO> getCompanyAvgPreScore(Integer demodayId);
	
	List<DemodayCompanyVO> getDemodayCompanies(Integer demodayId);
	
	List <DemodayCompanyVO> getSysDemodayCompanies(Integer demodayId,String orgName);
	
	List <DemodayCompanyVO> getSysDemodayCompanies(Integer demodayId,Integer start,Integer pageSize,String orgName);
	
	List<DemodayOrgVO> getDemodayOrgs(Integer demodayId);

	Demoday get(Integer demodayId);

	Demoday getByName(String name);

	DemodayDetailVO getDemodayDetai(Integer demodayId);

	List getXOrgList(Integer status);
	
	void addDemoday(Demoday demoday, List<Integer> orgIds);

	void updateDemoday(Demoday demoday);

	void updateDemodayOrg(Integer demodayId, Integer orgId, Integer status);

	void updateDemodayOrg(Integer demodayId, List<Integer> orgIds, Integer status);

	void updateDemodayCompanies(Integer demodayId, List<DemodayCompanyVO> demodayCompanyVOList);
	
	void updateDemodayCompany(Integer id,Integer scoringStatus);
	
	void updateDemodayCompany(List<Integer> ids,Integer scoringStatus);
	
	void updateDemodayCompanyJoinStatus(List<Integer> ids,Integer joinStatus);
	
	void removeDemodayCompany(Integer id);
	
	void updateSysDemodayCompanies(List<Integer> ids, Character pass);
}
