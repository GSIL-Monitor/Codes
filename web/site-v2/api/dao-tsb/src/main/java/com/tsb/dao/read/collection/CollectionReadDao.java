package com.tsb.dao.read.collection;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.collection.Collection;

public interface CollectionReadDao {
	
	Collection getById(Integer id);

	List<Collection> getByUserId(Integer userId);

	List<Collection> getCustomCols(@Param("userId") Integer userId, @Param("type") Integer type);

	List<Collection> getSysCols(@Param("userId") Integer userId, @Param("type") Integer type);
	
}
