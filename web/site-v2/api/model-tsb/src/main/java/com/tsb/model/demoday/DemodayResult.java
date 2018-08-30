package com.tsb.model.demoday;

import com.tsb.model.TimeModel;

public class DemodayResult extends TimeModel {
	private Integer id;
	private Integer organizationId;
	private Integer demodayCompanyId;
	private Integer result;
	private Integer createUser;
	private Integer modifyUser;

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public Integer getOrganizationId() {
		return organizationId;
	}

	public void setOrganizationId(Integer organizationId) {
		this.organizationId = organizationId;
	}

	public Integer getDemodayCompanyId() {
		return demodayCompanyId;
	}

	public void setDemodayCompanyId(Integer demodayCompanyId) {
		this.demodayCompanyId = demodayCompanyId;
	}

	public Integer getResult() {
		return result;
	}

	public void setResult(Integer result) {
		this.result = result;
	}

	public Integer getCreateUser() {
		return createUser;
	}

	public void setCreateUser(Integer createUser) {
		this.createUser = createUser;
	}

	public Integer getModifyUser() {
		return modifyUser;
	}

	public void setModifyUser(Integer modifyUser) {
		this.modifyUser = modifyUser;
	}

}
