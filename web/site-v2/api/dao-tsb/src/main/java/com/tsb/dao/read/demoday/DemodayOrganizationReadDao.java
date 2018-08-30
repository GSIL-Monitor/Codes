package com.tsb.dao.read.demoday;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.demoday.DemodayOrganization;

public interface DemodayOrganizationReadDao {
	List<DemodayOrganization> getByDemodayId(Integer demodayId);

	DemodayOrganization getDemodayOrg(@Param("demodayId") Integer demodayId, @Param("orgId") Integer orgId);

	DemodayOrganization getJoinDemodayOrg(@Param("demodayId") Integer demodayId, @Param("orgId") Integer orgId,
			@Param("status") Integer status);
	
	List<DemodayOrganization> getJoinOrgs(@Param("demodayId") Integer demodayId,@Param("status") Integer status);
	// 根据状态获取org的id
	List<Integer> getOrgIds(@Param("demodayId") Integer demodayId,@Param("status") Integer status);
}
