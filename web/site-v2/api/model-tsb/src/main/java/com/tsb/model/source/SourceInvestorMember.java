package com.tsb.model.source;

public class SourceInvestorMember extends SourceBasicModel{

	private Integer id;
	private Integer sourceInvestorId;
	private Integer investorMemberId;
	private String name;
	private String logo;
	private String position;
	private String domain;
	private String description;
	private String location;
	private String education;
	private String work;
	private String field;
	private Integer source;
	private String sourceId;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getSourceInvestorId() {
		return sourceInvestorId;
	}

	public void setSourceInvestorId(Integer sourceInvestorId) {
		this.sourceInvestorId = sourceInvestorId;
	}

	public Integer getInvestorMemberId() {
		return investorMemberId;
	}

	public void setInvestorMemberId(Integer investorMemberId) {
		this.investorMemberId = investorMemberId;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getLogo() {
		return logo;
	}

	public void setLogo(String logo) {
		this.logo = logo;
	}

	public String getPosition() {
		return position;
	}

	public void setPosition(String position) {
		this.position = position;
	}

	public String getDomain() {
		return domain;
	}

	public void setDomain(String domain) {
		this.domain = domain;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getLocation() {
		return location;
	}

	public void setLocation(String location) {
		this.location = location;
	}

	public String getEducation() {
		return education;
	}

	public void setEducation(String education) {
		this.education = education;
	}

	public String getWork() {
		return work;
	}

	public void setWork(String work) {
		this.work = work;
	}

	public String getField() {
		return field;
	}

	public void setField(String field) {
		this.field = field;
	}

	public Integer getSource() {
		return source;
	}

	public void setSource(Integer source) {
		this.source = source;
	}

	public String getSourceId() {
		return sourceId;
	}

	public void setSourceId(String sourceId) {
		this.sourceId = sourceId;
	}

}
