package com.tsb.company.service;

import java.util.List;
import java.util.Map;

import com.tsb.company.vo.DemodayCompanyVO;
import com.tsb.company.vo.DemodayResultVO;
import com.tsb.company.vo.DemodayVO;
import com.tsb.model.demoday.DemodayCompany;

@SuppressWarnings("rawtypes")
public interface DemodayService {
	
//	void getCompanyPrescore(Integer demodayId);

	DemodayVO getDemoday(Integer demodayId);

	List<DemodayVO> get();

	Map getPrescore(Integer userId, Integer demodayId, String code);

	List getPreScores(Integer userId, Integer demodayId);

	Map getScore(Integer userId, Integer demodayId, String code);

	List getScores(Integer userId, Integer demodayId);

	DemodayResultVO getResult(Integer userId, Integer demodayId, String code);
	
	Map getDemodayOrgs(Integer demodayId);
	
	List<DemodayCompanyVO> getDemodayCompanies(Integer demodayId);
	
	Map getDemodayCompany(Integer demodayId,Integer companyId,Integer userId);

	void preScore(Integer userId, Integer demodayId, String code, Integer score);

	void score(Integer userId, Integer demodayId, String code, List<Integer> scores);

	void invest(Integer userId, Integer demodayId, String code, Integer result);

	void updateDemodayOrgList(Integer demodayId, Integer status, List<String> orgNames);
	
	Integer addDemodayCompany(Integer demodayId,String code,Integer userId);
	
	Integer commitDemodayCompany(DemodayCompany  demodayCompany,Integer userId);
	
	void updateDemodayCompany(DemodayCompany demodayCompany);
	
	List notPassedList(Integer start,Integer pageSize,Integer userId,Integer demodayId);
	
	int countNotPassNum(Integer demodayId);
}
