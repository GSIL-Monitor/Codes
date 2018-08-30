package com.tsb.dao.write.company;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.CompanySector;

public interface CompanySectorWriteDao {
	public void insert(CompanySector companySector);
	public void update(CompanySector companySector);
	public void delete(Integer companyId);
	public void deleteOneSector(@Param("companyId")Integer companyId, @Param("sectorId")Integer sectorId);
}
