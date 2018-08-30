package com.tsb.model;

import java.sql.Timestamp;

public class TagsRel {

	private Integer id;
	private Integer tagId;
	private Integer tag2Id;
	private Float distance;
	private Timestamp createTime;
	private Timestamp modifyTime;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getTagId() {
		return tagId;
	}

	public void setTagId(Integer tagId) {
		this.tagId = tagId;
	}

	public Integer getTag2Id() {
		return tag2Id;
	}

	public void setTag2Id(Integer tag2Id) {
		this.tag2Id = tag2Id;
	}

	public Float getDistance() {
		return distance;
	}

	public void setDistance(Float distance) {
		this.distance = distance;
	}

	public Timestamp getCreateTime() {
		return createTime;
	}

	public void setCreateTime(Timestamp createTime) {
		this.createTime = createTime;
	}

	public Timestamp getModifyTime() {
		return modifyTime;
	}

	public void setModifyTime(Timestamp modifyTime) {
		this.modifyTime = modifyTime;
	}

}
