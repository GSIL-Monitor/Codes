package com.tsb.model.company;

import com.tsb.model.BasicModel;

public class ArtifactMarket extends BasicModel {

	private Integer id;
	private Integer artifactId;
	private String name;
	private String description;
	private String link;
	private String domain;
	private Integer type;
	private String others;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
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

	public String getDomain() {
		return domain;
	}

	public void setDomain(String domain) {
		this.domain = domain;
	}

	public Integer getType() {
		return type;
	}

	public void setType(Integer type) {
		this.type = type;
	}

	public String getOthers() {
		return others;
	}

	public void setOthers(String others) {
		this.others = others;
	}

}
