package com.tsb.admin.dao;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.admin.vo.ColdCallVO;

public interface ColdCallVOReadDao {
	
	List<ColdCallVO> getUnMatchedList(@Param("from") int from, @Param("pageSize") int pageSize);
	
	List<ColdCallVO> getmatchedList(@Param("from") int from, @Param("pageSize") int pageSize);
	
}
