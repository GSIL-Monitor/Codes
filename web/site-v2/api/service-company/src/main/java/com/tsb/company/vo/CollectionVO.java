package com.tsb.company.vo;

public class CollectionVO {
	
	private Integer id;
	private String name;
	private String description;
	private Float sort;
	// 用户是否关注了此collection（hot）
	private Character active;

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

	public Float getSort() {
		return sort;
	}

	public void setSort(Float sort) {
		this.sort = sort;
	}

	public Character getActive() {
		return active;
	}

	public void setActive(Character active) {
		this.active = active;
	}

}
