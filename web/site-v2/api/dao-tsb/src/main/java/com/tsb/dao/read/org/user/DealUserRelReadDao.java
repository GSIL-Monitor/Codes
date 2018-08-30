package com.tsb.dao.read.org.user;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.org.user.DealUserRel;

public interface DealUserRelReadDao {
	List<DealUserRel> listByDealId(Integer dealId);
	DealUserRel getByDealIdAndIdentify(@Param("dealId") Integer dealId, @Param("userIdentify") Integer userIdentify);
}
