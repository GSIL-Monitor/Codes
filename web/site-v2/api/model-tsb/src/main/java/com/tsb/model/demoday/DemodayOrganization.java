package com.tsb.model.demoday;

import com.tsb.model.TimeModel;

public class DemodayOrganization extends TimeModel {

	private Integer id;
	private Integer demodayId;
	private Integer organizationId;
	private Integer status;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getDemodayId() {
		return demodayId;
	}

	public void setDemodayId(Integer demodayId) {
		this.demodayId = demodayId;
	}

	public Integer getOrganizationId() {
		return organizationId;
	}

	public void setOrganizationId(Integer organizationId) {
		this.organizationId = organizationId;
	}

	public Integer getStatus() {
		return status;
	}

	public void setStatus(Integer status) {
		this.status = status;
	}

}
