package com.tsb.model.company;

import com.tsb.model.BasicModel;

public class Member extends BasicModel {

	private Integer id;
	private String name;
	private String education;
	private String workEmphasis;
	private String work;
	private String photo;
	private String email;
	private String phone;

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

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public String getPhone() {
		return phone;
	}

	public void setPhone(String phone) {
		this.phone = phone;
	}

}
