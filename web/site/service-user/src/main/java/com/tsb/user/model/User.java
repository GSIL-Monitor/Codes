package com.tsb.user.model;

import java.io.Serializable;

import com.tsb.user.model.BasicModel;

public class User extends BasicModel implements Serializable {
	private static final long serialVersionUID = -6258305783458545302L;
	
	private Integer id;
	private String username;
	private String password;
	private String email;
	private String phone;
	private Character active;
	public Integer getId() {
		return id;
	}
	public void setId(Integer id) {
		this.id = id;
	}
	public String getUsername() {
		return username;
	}
	public void setUsername(String username) {
		this.username = username;
	}
	public String getPassword() {
		return password;
	}
	public void setPassword(String password) {
		this.password = password;
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
	public Character getActive() {
		return active;
	}
	public void setActive(Character active) {
		this.active = active;
	}
	
}
