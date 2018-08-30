package com.crawler.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.crawler.model.IOS;

public interface IOSReadDao {
	List<IOS> get(@Param("tableId") int tableId, @Param("artifactId") int artifactId);

	List<IOS> getByType(@Param("tableId") int tableId, @Param("artifactId") int artifactId, @Param("type") int type);

	List<IOS> getByTypeExpand(@Param("tableId") int tableId, @Param("artifactId") int artifactId,
			@Param("type") int type, @Param("expand") int expand);
}
