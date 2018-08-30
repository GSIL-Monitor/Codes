package com.tsb.crawler.dao;

import java.util.List;

import com.tsb.model.News;

public interface NewsReadDao {
	List<News> get(String tableId, Integer companyId);
}
