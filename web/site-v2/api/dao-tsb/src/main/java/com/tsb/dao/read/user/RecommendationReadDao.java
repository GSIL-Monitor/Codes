package com.tsb.dao.read.user;

import java.util.List;

import com.tsb.model.user.Recommendation;

public interface RecommendationReadDao {
	List<Recommendation> get(Integer userId);
}
