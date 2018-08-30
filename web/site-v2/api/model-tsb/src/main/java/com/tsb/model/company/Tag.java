package com.tsb.model.company;

import com.tsb.model.BasicModel;

public class Tag extends BasicModel {

	private Integer id;
	private String name;
	private Integer type;
	private String weight;
	private Float novelty;

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

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

	public String getWeight() {
		return weight;
	}

	public void setWeight(String weight) {
		this.weight = weight;
	}

	public Float getNovelty() {
		return novelty;
	}

	public void setNovelty(Float novelty) {
		this.novelty = novelty;
	}

}
