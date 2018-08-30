package com.tsb.dao.read.user;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.user.UserSector;

public interface UserSectorReadDao {
	UserSector getBySectorId(@Param("sectorId")Integer sectorId, @Param("userId") Integer userId);
	List<UserSector> get(Integer userId);
}
