package com.tsb.company.dao;

import java.util.Date;
import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.company.vo.ColdcallVO;

public interface ColdcallVODao {
	int countAssigned(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("fromDate") Date fromDate, @Param("toDate") Date toDate);

	int countTODO(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("filter") int filter);
	List<ColdcallVO> listTODO(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("filter") int filter, @Param("from") int from, @Param("pageSize") int pageSize);

	int countDeclined(@Param("organizationId") int organizationId, @Param("userId") int userId);
	List<ColdcallVO> listDeclined(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("from") int from, @Param("pageSize") int pageSize);

	int countTODOSponsored(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("filter") int filter);
	List<ColdcallVO> listTODOSponsored(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("filter") int filter, @Param("from") int from, @Param("pageSize") int pageSize);
	
	int countSponsoredDeclined(@Param("organizationId") int organizationId, @Param("userId") int userId);
	List<ColdcallVO> listSponsoredDeclined(@Param("organizationId") int organizationId, @Param("userId") int userId, @Param("from") int from, @Param("pageSize") int pageSize);

	List<ColdcallVO> listTasks(@Param("organizationId") int organizationId, @Param("userId") int userId,  @Param("filter") int filter, @Param("from") int from, @Param("pageSize") int pageSize);
	
}
