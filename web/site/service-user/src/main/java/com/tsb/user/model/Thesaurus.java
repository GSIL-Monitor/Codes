package com.tsb.user.model;

import com.tsb.user.model.BasicModel;


public class Thesaurus extends BasicModel{
	private int termId;
	private String termName;
	private int termType;
	private float weight;
	private float hotness;
	
	public int getTermId() {
		return termId;
	}
	public void setTermId(int termId) {
		this.termId = termId;
	}
	public String getTermName() {
		return termName;
	}
	public void setTermName(String termName) {
		this.termName = termName;
	}
	public int getTermType() {
		return termType;
	}
	public void setTermType(int termType) {
		this.termType = termType;
	}
	public float getWeight() {
		return weight;
	}
	public void setWeight(float weight) {
		this.weight = weight;
	}
	public float getHotness() {
		return hotness;
	}
	public void setHotness(float hotness) {
		this.hotness = hotness;
	}
	
	
}
