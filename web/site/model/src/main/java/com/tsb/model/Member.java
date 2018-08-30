package com.tsb.model;

public class Member extends BasicModel{
	private Integer id;
	private String name;
	private String education;
	private String workEmphasis;
	private String work;
	private String photo;
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public String getName() {
		return name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getEducation() {
		return education;
	}
	public void setEducation(String education) {
		this.education = education;
	}
	public String getWorkEmphasis() {
		return workEmphasis;
	}
	public void setWorkEmphasis(String workEmphasis) {
		this.workEmphasis = workEmphasis;
	}
	public String getWork() {
		return work;
	}
	public void setWork(String work) {
		this.work = work;
	}
	public String getPhoto() {
		return photo;
	}
	public void setPhoto(String photo) {
		this.photo = photo;
	}
	
}
