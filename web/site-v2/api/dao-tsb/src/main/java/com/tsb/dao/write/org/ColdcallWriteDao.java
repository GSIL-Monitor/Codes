package com.tsb.dao.write.org;

import org.apache.ibatis.annotations.Param;

public interface ColdcallWriteDao {
	void decline(@Param("coldcallId")int coldcallId, @Param("declineId")int declineId);
}
