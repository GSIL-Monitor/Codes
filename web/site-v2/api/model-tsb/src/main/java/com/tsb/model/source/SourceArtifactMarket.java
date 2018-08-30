package com.tsb.model.source;

public class SourceArtifactMarket extends SourceBasicModel {

	private Integer id;
	private Integer artifactMarketId;
	private String link;
	private String description;
	private Integer source;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getArtifactMarketId() {
		return artifactMarketId;
	}

	public void setArtifactMarketId(Integer artifactMarketId) {
		this.artifactMarketId = artifactMarketId;
	}

	public String getLink() {
		return link;
	}

	public void setLink(String link) {
		this.link = link;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public Integer getSource() {
		return source;
	}

	public void setSource(Integer source) {
		this.source = source;
	}

}
