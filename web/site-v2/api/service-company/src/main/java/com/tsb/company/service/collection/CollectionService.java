package com.tsb.company.service.collection;

import java.util.List;
import java.util.Map;

@SuppressWarnings("rawtypes")
public interface CollectionService {
	int countTimeLie(int userId);

	int countCollComp(int collectionId);

	Map getCollections(Integer userId);

	Map getTimeLineComp(Integer userId, int start, int pageSize);

	Map getCollCompList(Integer collectionId, Integer userId, int start, int pageSize);

	Map getSortCompList(Integer userId, Integer sector, Integer location, Integer round, Integer collectionId,
			int start, int pageSize);
	
	int countSort(Integer userId, Integer sector, Integer location, Integer round, Integer collectionId);

	void updateCollection(Integer collectionId, Integer userId, Character active);

	void addCollection(List<Integer> sectors, List<Integer> locations, List<Integer> rounds, List<Integer> investors,
			List<Integer> education, List<Integer> works, String name, int userId);
	
	void followCollection(Integer collectionId,Integer userId);
	
	void unFollowCollection(Integer collectionId,Integer userId);
}
