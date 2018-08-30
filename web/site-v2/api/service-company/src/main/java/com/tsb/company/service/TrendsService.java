package com.tsb.company.service;

import java.util.Map;

@SuppressWarnings("rawtypes")
public interface TrendsService {
	Map getTrends(Integer companyId ,Integer artifactId,Integer artifactType,Integer expand);
}
