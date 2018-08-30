package com.tsb.dao.read.company;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.ArtifactPic;

@SuppressWarnings("rawtypes")
public interface ArtifactPicReadDao {

	List<ArtifactPic> get(Integer aritfactId);

	List<ArtifactPic> getByIds(@Param("ids") List artifactIds);

}
