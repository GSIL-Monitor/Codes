package com.tsb.model.vo;

import java.util.List;

import com.tsb.model.Artifact;
import com.tsb.model.Company;
import com.tsb.model.CompanyAlias;
import com.tsb.model.Domain;
import com.tsb.model.Footprint;
import com.tsb.model.Funding;
import com.tsb.model.News;
import com.tsb.model.Product;
import com.tsb.model.source.SourceCompany;
import com.tsb.model.user.UserCompanyFollow;
import com.tsb.model.user.UserCompanyNote;

public class CompanyVO {

	private Company company;
	// related column
	private String location;
	// keywords
	private String keywords;

	private List<CompanyTagRelVO> tagRelList;
	// funding
	private List<Funding> fundingList;
	// product
	private List<Product> prductList;
	// artifact
	private List<Artifact> artifactList;
	// news
	private List<News> newsList;
	// footprint
	private List<Footprint> footprintList;
	// domain
	private List<Domain> domainList;
	// source company
	private List<SourceCompany> sourceCompanyList;

	// companies rel
	private List<CompanyAlias> companyAliasList;
	// TO DO
	private List<CompanyVO> relCompanies;
	// user company follow
	private UserCompanyFollow userCompanyFollow;
	// user company note
	private UserCompanyNote userCompanyNote;

	public Company getCompany() {
		return company;
	}

	public void setCompany(Company company) {
		this.company = company;
	}

	public String getLocation() {
		return location;
	}

	public void setLocation(String location) {
		this.location = location;
	}

	public String getKeywords() {
		return keywords;
	}

	public void setKeywords(String keywords) {
		this.keywords = keywords;
	}

	public List<CompanyTagRelVO> getTagRelList() {
		return tagRelList;
	}

	public void setTagRelList(List<CompanyTagRelVO> tagRelList) {
		this.tagRelList = tagRelList;
	}

	public List<Funding> getFundingList() {
		return fundingList;
	}

	public void setFundingList(List<Funding> fundingList) {
		this.fundingList = fundingList;
	}

	public List<Product> getPrductList() {
		return prductList;
	}

	public void setPrductList(List<Product> prductList) {
		this.prductList = prductList;
	}

	public List<Artifact> getArtifactList() {
		return artifactList;
	}

	public void setArtifactList(List<Artifact> artifactList) {
		this.artifactList = artifactList;
	}

	public List<News> getNewsList() {
		return newsList;
	}

	public void setNewsList(List<News> newsList) {
		this.newsList = newsList;
	}

	public List<Footprint> getFootprintList() {
		return footprintList;
	}

	public void setFootprintList(List<Footprint> footprintList) {
		this.footprintList = footprintList;
	}

	public List<Domain> getDomainList() {
		return domainList;
	}

	public void setDomainList(List<Domain> domainList) {
		this.domainList = domainList;
	}

	public List<SourceCompany> getSourceCompanyList() {
		return sourceCompanyList;
	}

	public void setSourceCompanyList(List<SourceCompany> sourceCompanyList) {
		this.sourceCompanyList = sourceCompanyList;
	}

	public List<CompanyAlias> getCompanyAliasList() {
		return companyAliasList;
	}

	public void setCompanyAliasList(List<CompanyAlias> companyAliasList) {
		this.companyAliasList = companyAliasList;
	}

	public List<CompanyVO> getRelCompanies() {
		return relCompanies;
	}

	public void setRelCompanies(List<CompanyVO> relCompanies) {
		this.relCompanies = relCompanies;
	}

	public UserCompanyFollow getUserCompanyFollow() {
		return userCompanyFollow;
	}

	public void setUserCompanyFollow(UserCompanyFollow userCompanyFollow) {
		this.userCompanyFollow = userCompanyFollow;
	}

	public UserCompanyNote getUserCompanyNote() {
		return userCompanyNote;
	}

	public void setUserCompanyNote(UserCompanyNote userCompanyNote) {
		this.userCompanyNote = userCompanyNote;
	}

}
