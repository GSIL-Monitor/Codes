package com.tsb.admin.service;

import java.util.List;

import com.tsb.admin.vo.ColdCallVO;

public interface ColdCallService {
	Integer totalColdCall();

	Integer coutMatchedColdCall();

	Integer coutUnmatchedColdCall();

	List<ColdCallVO> getUnmatchedList(Integer from, Integer pageSize);
	
	List<ColdCallVO> getmatchedList(Integer from, Integer pageSize);
}
