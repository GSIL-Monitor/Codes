package com.tsb.dao.read.company;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.CompanySector;

public interface CompanySectorReadDao {
	List<CompanySector> get(Integer companyId);
	CompanySector getBySectorId(@Param("companyId")Integer companyId, @Param("sectorId")Integer sectorId);
}
