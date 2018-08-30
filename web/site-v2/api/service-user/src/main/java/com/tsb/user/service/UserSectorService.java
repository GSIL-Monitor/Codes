package com.tsb.user.service;

import java.util.List;

import com.tsb.model.user.UserSector;

public interface UserSectorService {
	List<UserSector> get(Integer userId);
	void add(List<Integer> sectorIds, Integer userId);
	void update(List newIds, List deleteIds, int userId);
	void delete(List<Integer> sectorIds, Integer userId);
}
