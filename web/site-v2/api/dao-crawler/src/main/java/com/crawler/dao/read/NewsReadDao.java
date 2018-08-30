package com.crawler.dao.read;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.crawler.model.News;

public interface NewsReadDao {
	List<News> get(@Param("tableId")int tableId, @Param("companyId")int companyId);
	News getByNewsId(@Param("tableId")int tableId, @Param("newsId")int newsId);
}
