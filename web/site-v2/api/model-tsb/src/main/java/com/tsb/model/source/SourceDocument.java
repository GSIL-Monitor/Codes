package com.tsb.model.source;

public class SourceDocument extends SourceBasicModel {

	private Integer id;
	private Integer sourceCompanyId;
	private Integer documentId;
	private String name;
	private String description;
	private String link;
	private Integer type;

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

	public Integer getDocumentId() {
		return documentId;
	}

	public void setDocumentId(Integer documentId) {
		this.documentId = documentId;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getLink() {
		return link;
	}

	public void setLink(String link) {
		this.link = link;
	}

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

}
