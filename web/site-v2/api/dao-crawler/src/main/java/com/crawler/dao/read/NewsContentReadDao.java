package com.crawler.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.crawler.model.NewsContent;

public interface NewsContentReadDao {
	List<NewsContent> get(@Param("tableId")int tableId, @Param("newsId")int newsId);
}
