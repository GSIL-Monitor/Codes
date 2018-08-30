package com.tsb.model.company;

import com.tsb.model.BasicModel;

public class ArtifactPic extends BasicModel {

	private Integer id;
	private Integer artifactId;
	private Integer artifactMarketId;
	private String link;
	private Integer rank;

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

	public Integer getRank() {
		return rank;
	}

	public void setRank(Integer rank) {
		this.rank = rank;
	}

}
