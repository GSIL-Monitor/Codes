package com.tsb.crawler.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document
public class Alexa {
	@Id
	private String id;
	private String domain;
	private String search_visits;
	private String global_rank;
	private String country_rank;
	private String date;
	private String[] page_view;

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public String getDomain() {
		return domain;
	}

	public void setDomain(String domain) {
		this.domain = domain;
	}

	public String getSearch_visits() {
		return search_visits;
	}

	public void setSearch_visits(String search_visits) {
		this.search_visits = search_visits;
	}

	

	public String getGlobal_rank() {
		return global_rank;
	}

	public void setGlobal_rank(String global_rank) {
		this.global_rank = global_rank;
	}

	public String getCountry_rank() {
		return country_rank;
	}

	public void setCountry_rank(String country_rank) {
		this.country_rank = country_rank;
	}

	public String getDate() {
		return date;
	}

	public void setDate(String date) {
		this.date = date;
	}

	public String[] getPage_view() {
		return page_view;
	}

	public void setPage_view(String[] page_view) {
		this.page_view = page_view;
	}

}
