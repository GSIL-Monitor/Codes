package com.crawler.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.crawler.model.Alexa;

public interface AlexaReadDao {
	List<Alexa> get(@Param("tableId") int tableId, @Param("artifactId") int artifactId);

	List<Alexa> getByExpand(@Param("tableId") int tableId, @Param("artifactId") int artifactId,
			@Param("expand") int expand);
}
