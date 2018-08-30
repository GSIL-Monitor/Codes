package com.tsb.company.service;

import java.util.List;

import com.tsb.model.company.Sector;

@SuppressWarnings("rawtypes")
public interface SectorService {
	List<Sector> get();
	List<Sector> get(Integer id);
	List<Sector> getByCompanyId(Integer companyId);
	
	void addCompanySector(Integer companyId,List sectorIds,Integer userId);
	void updateCompanySector(List<Integer> sectorIds, Integer companyId,  Integer userId);
	Sector updateSector(Integer companyId, Integer id, Integer oldId, Integer userId);
}
