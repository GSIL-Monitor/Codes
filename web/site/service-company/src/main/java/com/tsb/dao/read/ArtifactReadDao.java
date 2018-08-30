package com.tsb.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.Artifact;

public interface ArtifactReadDao {

	List<Artifact> getByCompanyId(Integer companyId);

	List<Artifact> getByCompIdAndType(@Param("companyId") int companyId, @Param("type") int artifactType);

}
