package com.crawler.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.crawler.model.Android;

public interface AndroidReadDao {
	List<Android> get(@Param("tableId") int tableId, @Param("artifactId") int artifactId);

	List<Android> getByType(@Param("tableId") int tableId, @Param("artifactId") int artifactId,
			@Param("type") int type);

	List<Android> getByTypeExpand(@Param("tableId") int tableId, @Param("artifactId") int artifactId,
			@Param("type") int type, @Param("expand") int expand);
}
