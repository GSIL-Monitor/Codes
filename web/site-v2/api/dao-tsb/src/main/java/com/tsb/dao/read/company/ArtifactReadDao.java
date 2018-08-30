package com.tsb.dao.read.company;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.Artifact;

@SuppressWarnings("rawtypes")
public interface ArtifactReadDao {

	Artifact getById(Integer id);

	List<Artifact> getByCompanyId(	@Param("companyId") Integer companyId,
									@Param("start") Integer start,
									@Param("pageSize") Integer pageSize);

	List<Artifact> getByCompIdAndType(  @Param("companyId") int companyId,
									    @Param("type") int artifactType,
									    @Param("start") Integer start,
										@Param("pageSize") Integer pageSize);

	List getTypes(int companyId);
	
	int countByCompanyId(int companyId);
	
	int countByCompanyIdAndType(@Param("companyId") int companyId, @Param("type") int artifactType);

}
