package com.tsb.model;

import java.sql.Date;

public class Domain extends BasicModel {
	private Integer id;
	private Integer companyId;
	private String domain;
	private String organizer;
	private String organizerType;
	private String beianhao;
	private String mainBeianhao;
	private String websiteName;
	private String homepage;
	private Date beianDate;
	private Character expire;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getCompanyId() {
		return companyId;
	}

	public void setCompanyId(Integer companyId) {
		this.companyId = companyId;
	}

	public String getDomain() {
		return domain;
	}

	public void setDomain(String domain) {
		this.domain = domain;
	}

	public String getOrganizer() {
		return organizer;
	}

	public void setOrganizer(String organizer) {
		this.organizer = organizer;
	}

	public String getOrganizerType() {
		return organizerType;
	}

	public void setOrganizerType(String organizerType) {
		this.organizerType = organizerType;
	}

	public String getBeianhao() {
		return beianhao;
	}

	public void setBeianhao(String beianhao) {
		this.beianhao = beianhao;
	}

	public String getMainBeianhao() {
		return mainBeianhao;
	}

	public void setMainBeianhao(String mainBeianhao) {
		this.mainBeianhao = mainBeianhao;
	}

	public String getWebsiteName() {
		return websiteName;
	}

	public void setWebsiteName(String websiteName) {
		this.websiteName = websiteName;
	}

	public String getHomepage() {
		return homepage;
	}

	public void setHomepage(String homepage) {
		this.homepage = homepage;
	}

	public Date getBeianDate() {
		return beianDate;
	}

	public void setBeianDate(Date beianDate) {
		this.beianDate = beianDate;
	}

	public Character getExpire() {
		return expire;
	}

	public void setExpire(Character expire) {
		this.expire = expire;
	}

}
