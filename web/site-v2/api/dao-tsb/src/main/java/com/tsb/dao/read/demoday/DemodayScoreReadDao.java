package com.tsb.dao.read.demoday;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.demoday.DemodayScore;

public interface DemodayScoreReadDao {
	List<DemodayScore> get(Integer dealDemodayId);

	DemodayScore getDemodayScore(@Param("dealDemodayId") Integer dealDemodayId, @Param("userId") Integer userId);
}
