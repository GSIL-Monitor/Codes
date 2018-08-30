package com.tsb.company.vo;

import java.util.List;

import com.crawler.model.News;
import com.crawler.model.NewsContent;

public class NewsVO {
	private News news;
	private List<NewsContent> contents;
	public News getNews() {
		return news;
	}
	public void setNews(News news) {
		this.news = news;
	}
	public List<NewsContent> getContents() {
		return contents;
	}
	public void setContents(List<NewsContent> contents) {
		this.contents = contents;
	}
	
}
