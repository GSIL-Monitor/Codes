package com.tsb.dao.read.org;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.org.ColdcallForward;

public interface ColdcallForwardReadDao {
	List<ColdcallForward> get(int coldcallId);
	ColdcallForward getColdcallForward(@Param("coldcallId") int coldcallId,@Param("fromUserId") int fromUserId,
			@Param("toUserId") int toUserId);
}
