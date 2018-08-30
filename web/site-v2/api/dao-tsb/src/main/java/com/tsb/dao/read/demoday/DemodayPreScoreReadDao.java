package com.tsb.dao.read.demoday;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.demoday.DemodayPreScore;

public interface DemodayPreScoreReadDao {

	List<DemodayPreScore> get(Integer dealDemodayId);

	DemodayPreScore getDemodayPrescore(@Param("dealDemodayId") Integer dealDemodayId, @Param("userId") Integer userId);


}
