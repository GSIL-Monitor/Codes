package com.tsb.company.service;

import java.util.List;
import java.util.Map;

import com.tsb.company.vo.ArtifactVO;
import com.tsb.model.company.Artifact;

@SuppressWarnings("rawtypes")
public interface ArtifactService {
	
	Map getArtifacts(int companyId, int start, int pageSize);
	List getArtifactTypeList(int companyId);
	int countArtifactType(int companyId, int atType);
	ArtifactVO getArtifact(int id);
	void add(List<Artifact> artifactList, Integer sourceCompanyId);
}
