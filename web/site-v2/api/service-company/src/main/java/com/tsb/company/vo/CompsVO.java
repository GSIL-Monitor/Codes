package com.tsb.company.vo;

import java.util.List;

import com.tsb.model.company.Company;
import com.tsb.model.company.Sector;
import com.tsb.model.company.Tag;

public class CompsVO {
	private Company company;
	private String location;
	private List<Tag> tags;
	private List<FundingVO> fundings;
	private List<Sector> sectors;
	
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
	public List<Tag> getTags() {
		return tags;
	}
	public void setTags(List<Tag> tags) {
		this.tags = tags;
	}
	public List<FundingVO> getFundings() {
		return fundings;
	}
	public void setFundings(List<FundingVO> fundings) {
		this.fundings = fundings;
	}
	public List<Sector> getSectors() {
		return sectors;
	}
	public void setSectors(List<Sector> sectors) {
		this.sectors = sectors;
	}
	
	
}
