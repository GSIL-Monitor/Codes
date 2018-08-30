package com.tsb.company.vo;

import com.tsb.model.company.Job;

public class JobVO {
	private Job job;
	private String location;
	public Job getJob() {
		return job;
	}
	public void setJob(Job job) {
		this.job = job;
	}
	public String getLocation() {
		return location;
	}
	public void setLocation(String location) {
		this.location = location;
	}
	
}
