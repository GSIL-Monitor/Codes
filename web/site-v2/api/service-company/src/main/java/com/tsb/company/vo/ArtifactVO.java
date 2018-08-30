package com.tsb.company.vo;

import java.util.List;

import com.tsb.model.company.Artifact;
import com.tsb.model.company.ArtifactPic;

public class ArtifactVO {

	private Artifact artifact;
	private List<ArtifactPic> pics;

	public Artifact getArtifact() {
		return artifact;
	}

	public void setArtifact(Artifact artifact) {
		this.artifact = artifact;
	}

	public List<ArtifactPic> getPics() {
		return pics;
	}

	public void setPics(List<ArtifactPic> pics) {
		this.pics = pics;
	}

}
