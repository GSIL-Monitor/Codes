package com.tsb.dao.read.collection;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.collection.CollectionCompanyRel;

public interface CollectionCompanyRelReadDao {
	List<CollectionCompanyRel> getColComRelByUserId(@Param("userId") int userId, @Param("start") int start,
			@Param("pageSize") int pageSize);

	List<CollectionCompanyRel> getColComRelByCollectionId(@Param("collectionId") Integer collectionId,
			@Param("start") int start, @Param("pageSize") int pageSize);

	List<Integer> getCompanyIds(Integer collectionId);

	int countTimeLine(int userId);

	int countCollComp(int collectionId);

	int countSort(@Param("userId") int userId, @Param("sector") int sector, @Param("location") int location,
			@Param("round") int round);

	int countColCompSort(@Param("sector") int sector, @Param("location") int location,
			@Param("round") int round, @Param("collectionId") Integer collectionId);

}
