package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.Sector;

public interface SectorReadDao {
	List<Sector> get();
	List<Sector> getByParentId(Integer id);
	Sector getById(Integer id);
	
}
