package com.tsb.model.source;

import java.sql.Date;

public class SourceArtifact extends SourceBasicModel {

	private Integer id;
	private Integer sourceCompanyId;
	private Integer artifactId;
	private String name;
	private String description;
	private String link;
	private Integer type;
	private Integer rank;
	private Date rankDate;

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

	public Integer getArtifactId() {
		return artifactId;
	}

	public void setArtifactId(Integer artifactId) {
		this.artifactId = artifactId;
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

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

	public Integer getRank() {
		return rank;
	}

	public void setRank(Integer rank) {
		this.rank = rank;
	}

	public Date getRankDate() {
		return rankDate;
	}

	public void setRankDate(Date rankDate) {
		this.rankDate = rankDate;
	}

}
