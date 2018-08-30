package com.tsb.dao.read.org.user;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.org.user.DealUserScore;

@SuppressWarnings("rawtypes")
public interface DealUserScoreReadDao {
	List listByUserId(Integer userId);

	List<DealUserScore> listByDealId(Integer dealId);

	List listByDealIdAndType(Integer dealId, Integer type);

	DealUserScore getByUserIdAndDealId(@Param("userId") Integer userId, @Param("dealId") Integer dealId);
}
