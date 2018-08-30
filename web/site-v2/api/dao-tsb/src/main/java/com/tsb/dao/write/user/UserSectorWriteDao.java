package com.tsb.dao.write.user;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.user.UserSector;

public interface UserSectorWriteDao {
	void insert(UserSector userSector);
	void update(UserSector userSector);
	void delete(@Param("userId")Integer userId, @Param("sectorId")Integer sectorId);
}
