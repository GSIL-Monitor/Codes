package com.tsb.dao.read.demoday;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.demoday.DemodayResult;

public interface DemodayResultReadDao {
	List<DemodayResult> get(Integer demodayCompanyId);

	DemodayResult getDemodayResult(@Param("demodayCompanyId") Integer demodayCompanyId,
			@Param("organizationId") Integer organizationId);

}
