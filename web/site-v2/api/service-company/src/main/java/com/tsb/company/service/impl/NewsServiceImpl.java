package com.tsb.company.service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.crawler.dao.read.CompanyIndexReadDao;
import com.crawler.dao.read.NewsContentReadDao;
import com.crawler.dao.read.NewsReadDao;
import com.crawler.model.CompanyIndex;
import com.tsb.company.service.NewsService;
import com.tsb.company.vo.NewsVO;

@Service
public class NewsServiceImpl implements NewsService{

	@Autowired
	private CompanyIndexReadDao companyIndexReadDao;
	
	@Autowired
	private NewsReadDao newsReadDao;
	
	@Autowired
	private NewsContentReadDao newsContentReadDao;
	
	@Override
	public List get(int companyId) {
		CompanyIndex companyIndex = companyIndexReadDao.get(companyId);
		if(companyIndex != null){
			int tableId = companyIndex.getNews();
			if(tableId > 0)
				return newsReadDao.get(tableId, companyId);
		}
		return null;
	}

	@Override
	public NewsVO getVO(int companyId, int newsId) {
		CompanyIndex companyIndex = companyIndexReadDao.get(companyId);
		if(companyIndex != null){
			int tableId = companyIndex.getNews();
			NewsVO newsVO = new NewsVO();
			newsVO.setNews(newsReadDao.getByNewsId(tableId, newsId));
			newsVO.setContents(newsContentReadDao.get(tableId, newsId));
			return newsVO;
		}
		return null;
	}

}
