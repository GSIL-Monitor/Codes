package com.tsb.dao.read.company;

import java.util.List;

import com.tsb.model.company.ArtifactMarket;

public interface ArtifactMarketReadDao {

	List<ArtifactMarket> get(Integer artifactId);
}
