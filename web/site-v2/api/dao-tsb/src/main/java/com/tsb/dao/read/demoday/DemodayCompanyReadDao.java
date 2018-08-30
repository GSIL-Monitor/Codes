package com.tsb.dao.read.demoday;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.demoday.DemodayCompany;

public interface DemodayCompanyReadDao {

	List<DemodayCompany> getByDemodayId(Integer demodayId);

	List<DemodayCompany> getRidCompId(@Param("demodayId") Integer demodayId, @Param("companyId") Integer companyId);

	DemodayCompany getDemodayCompany(@Param("demodayId") Integer demodayId, @Param("companyId") Integer companyId);

	DemodayCompany getById(Integer id);
	
	int getNotPassNum(Integer demodayId);
}
