package com.tsb.company.service;

import java.util.List;

import com.tsb.company.vo.DealNoteVO;
import com.tsb.company.vo.DealUserScoreVO;
import com.tsb.model.org.user.DealNote;


@SuppressWarnings("rawtypes")
public interface UserDealService {
	List getRelDeals(Integer userId);
	DealNote getDealNote(Integer userId);
	
	List<DealNoteVO> getDealNote(Integer userId,String code);
	List<DealUserScoreVO> getDealUserScore (Integer userId,Integer companyId);
	
	/*** write ***/
	void createNewDeal(Integer userId, Integer companyId, Integer score);
	void addDealScore(Integer userId, Integer dealId);
	void addDealNote(Integer userId, Integer dealId);
	
	void updateDealScore(Integer userId, Integer dealId);
	void updateDealNote(Integer userId, Integer dealId);
	
	void deleteDealNote(Integer userId, Integer dealId);
	
	void modifyDealScore(Integer userId,Integer companyId,Integer score,Integer type);
	void modifyDealNote(Integer userId, String code,Integer noteId,String note);
	void deleteDealNote(Integer noteId);
	void addDeal(Integer companyId,Integer orgId,Integer userId,Integer coldcallId);
	
}
