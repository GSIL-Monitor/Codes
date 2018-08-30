package com.tsb.model.collection;

import com.tsb.model.BasicModel;

public class CollectionCompanyRel extends BasicModel {
	private Integer id;
	private Integer collectionId;
	private Integer companyId;
	private Float sort;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getCollectionId() {
		return collectionId;
	}

	public void setCollectionId(Integer collectionId) {
		this.collectionId = collectionId;
	}

	public Integer getCompanyId() {
		return companyId;
	}

	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}

	public Float getSort() {
		return sort;
	}

	public void setSort(Float sort) {
		this.sort = sort;
	}

}
