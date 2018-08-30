package com.tsb.model.collection;

import com.tsb.model.BasicModel;

public class Collection extends BasicModel {
	private Integer id;
	private String name;
	private String description;
	private Integer type;
	private Float sort;
	private Character mark;
	private String rule;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}


	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

	public Float getSort() {
		return sort;
	}

	public void setSort(Float sort) {
		this.sort = sort;
	}

	public Character getMark() {
		return mark;
	}

	public void setMark(Character mark) {
		this.mark = mark;
	}

	public String getRule() {
		return rule;
	}

	public void setRule(String rule) {
		this.rule = rule;
	}

}
