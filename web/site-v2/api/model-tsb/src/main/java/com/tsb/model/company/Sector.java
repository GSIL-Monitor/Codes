package com.tsb.model.company;

import com.tsb.model.BasicModel;

public class Sector extends BasicModel {
	private Integer id;
	private String sectorName;
	private Integer level;
	private Integer parentId;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public String getSectorName() {
		return sectorName;
	}

	public Integer getLevel() {
		return level;
	}

	public void setLevel(Integer level) {
		this.level = level;
	}

	public Integer getParentId() {
		return parentId;
	}

	public void setParentId(Integer parentId) {
		this.parentId = parentId;
	}

	public void setSectorName(String sectorName) {
		this.sectorName = sectorName;
	}

}
