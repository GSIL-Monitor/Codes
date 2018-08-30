package com.tsb.crawler.service;

import java.util.List;

import com.tsb.model.News;

public interface NewsService {
	List<News> get(Integer companyId);
}
