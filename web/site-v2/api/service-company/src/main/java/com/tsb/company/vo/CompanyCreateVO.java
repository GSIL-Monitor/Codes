package com.tsb.company.vo;

import java.util.List;

import com.tsb.model.company.Artifact;
import com.tsb.model.company.Company;
import com.tsb.model.company.Document;
import com.tsb.model.company.Member;

public class CompanyCreateVO {
	private Company company;
	private Member member;
	private List<Artifact> artifacts;
	private Document document;

	public Company getCompany() {
		return company;
	}

	public void setCompany(Company company) {
		this.company = company;
	}

	public Member getMember() {
		return member;
	}

	public void setMember(Member member) {
		this.member = member;
	}

	public List<Artifact> getArtifacts() {
		return artifacts;
	}

	public void setArtifacts(List<Artifact> artifacts) {
		this.artifacts = artifacts;
	}

	public Document getDocument() {
		return document;
	}

	public void setDocument(Document document) {
		this.document = document;
	}

	
}
