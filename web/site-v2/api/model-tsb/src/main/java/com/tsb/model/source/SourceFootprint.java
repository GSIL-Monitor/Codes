package com.tsb.model.source;

public class SourceFootprint extends SourceBasicModel {

	private Integer id;
	private Integer sourceCompanyId;
	private Integer footprintId;
	private String footDate;
	private String description;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getSourceCompanyId() {
		return sourceCompanyId;
	}

	public void setSourceCompanyId(Integer sourceCompanyId) {
		this.sourceCompanyId = sourceCompanyId;
	}

	public Integer getFootprintId() {
		return footprintId;
	}

	public void setFootprintId(Integer footprintId) {
		this.footprintId = footprintId;
	}

	public String getFootDate() {
		return footDate;
	}

	public void setFootDate(String footDate) {
		this.footDate = footDate;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

}
