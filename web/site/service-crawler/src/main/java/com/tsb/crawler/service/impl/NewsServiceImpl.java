package com.tsb.crawler.service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.crawler.dao.NewsReadDao;
import com.tsb.crawler.service.NewsService;
import com.tsb.model.News;

@Service
public class NewsServiceImpl implements NewsService{

	@Autowired
	private NewsReadDao newsReadDao;
	
	@Override
	public List<News> get(Integer companyId) {
		int tableId = companyId%100;
		return newsReadDao.get(tableId+"", companyId);
	}

}
