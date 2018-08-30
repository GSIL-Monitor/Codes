package com.tsb.admin.vo;

import java.util.List;

import com.tsb.model.demoday.Demoday;

public class DemodayDetailVO {

	private Demoday demoday;
	// 所有参加的Xorg--包括参加的和不参加的
	private List<DemodayOrgVO> demodayOrgs;
	// demoday所有的company
	private List<DemodayCompanyVO> demodayCompanies;

	public Demoday getDemoday() {
		return demoday;
	}

	public void setDemoday(Demoday demoday) {
		this.demoday = demoday;
	}

	public List<DemodayOrgVO> getDemodayOrgs() {
		return demodayOrgs;
	}

	public void setDemodayOrgs(List<DemodayOrgVO> demodayOrgs) {
		this.demodayOrgs = demodayOrgs;
	}

	public List<DemodayCompanyVO> getDemodayCompanies() {
		return demodayCompanies;
	}

	public void setDemodayCompanies(List<DemodayCompanyVO> demodayCompanies) {
		this.demodayCompanies = demodayCompanies;
	}

}
