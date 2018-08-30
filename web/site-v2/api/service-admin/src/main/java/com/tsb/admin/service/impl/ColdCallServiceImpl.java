package com.tsb.admin.service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.admin.dao.ColdCallVOReadDao;
import com.tsb.admin.service.ColdCallService;
import com.tsb.admin.vo.ColdCallVO;
import com.tsb.dao.read.org.ColdcallCompanyRelReadDao;
import com.tsb.dao.read.org.ColdcallReadDao;
@Service
public class ColdCallServiceImpl implements ColdCallService {
	@Autowired
	private ColdcallReadDao coldCallReadDao;
	@Autowired
	private ColdcallCompanyRelReadDao coldcallCompanyReadDao; 
	@Autowired
	private ColdCallVOReadDao  coldCallVOReadDao;
	@Override
	public Integer totalColdCall() {
	
		return coldCallReadDao.getTotal();
	}
	@Override
	public Integer coutMatchedColdCall() {
		
		return coldcallCompanyReadDao.getMatchedColdCall();
	}
	@Override
	public Integer coutUnmatchedColdCall() {
		
		return coldCallReadDao.getUnMatched();
	}
	@Override
	public List<ColdCallVO> getUnmatchedList(Integer from, Integer pageSize) {
		
		return coldCallVOReadDao.getUnMatchedList(from, pageSize);
	}
	@Override
	public List<ColdCallVO> getmatchedList(Integer from, Integer pageSize) {
		
		return coldCallVOReadDao.getmatchedList(from, pageSize);
	}

}
