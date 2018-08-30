package com.tsb.model.crowdfunding;

import com.tsb.model.BasicModel;

public class SourceCfDocument extends BasicModel {

	private Integer id;
	private Integer sourceCfId;
	private Integer documentId;
	private String name;
	private String description;
	private String link;
	private Integer rank;
	private String sourceId;
	private Integer type;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getSourceCfId() {
		return sourceCfId;
	}

	public void setSourceCfId(Integer sourceCfId) {
		this.sourceCfId = sourceCfId;
	}

	public Integer getDocumentId() {
		return documentId;
	}

	public void setDocumentId(Integer documentId) {
		this.documentId = documentId;
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

	public String getLink() {
		return link;
	}

	public void setLink(String link) {
		this.link = link;
	}

	public Integer getRank() {
		return rank;
	}

	public void setRank(Integer rank) {
		this.rank = rank;
	}

	public String getSourceId() {
		return sourceId;
	}

	public void setSourceId(String sourceId) {
		this.sourceId = sourceId;
	}

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

}
