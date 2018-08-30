package com.tsb.company.dao;

import java.util.Date;
import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.company.vo.DealScoreVO;

public interface DealScoreVODao {
	int countAssigned(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("type") int type, @Param("fromDate") Date fromDate, @Param("toDate") Date toDate);
	
	int countTODO(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("type") int type, @Param("filter") int filter);
	List<DealScoreVO> listTODO(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("type") int type, @Param("filter") int filter, @Param("from") int from, @Param("pageSize") int pageSize);
	
	DealScoreVO getNextScoring(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("companyId") int exceptCompanyId);
}
