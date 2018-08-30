package com.tsb.dao.read.collection;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.collection.CollectionUserRel;

public interface CollectionUserRelReadDao {
	CollectionUserRel getByUserIdColId(@Param("userId") Integer userId,@Param("collectionId")Integer collectionId);
}
