package com.tsb.company.service;

import java.util.List;

import com.tsb.model.company.Footprint;

@SuppressWarnings("rawtypes")
public interface FootprintService {
	List get(int companyId);
	void addFootprints(List<Footprint> footprints, Integer userId);
	void updateFootprints(List<Footprint> footprints, Integer userId);
	void deleteFootprints(List<Integer> ids,  Integer userId);
}
