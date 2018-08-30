package com.tsb.company.vo;

import java.util.List;

import com.tsb.model.demoday.Demoday;
import com.tsb.model.demoday.DemodayCompany;

public class DemodayVO {
	// demo day name
	private Demoday demoday;
	private List<DemodayCompany> demodayCompanies;

	public Demoday getDemoday() {
		return demoday;
	}

	public void setDemoday(Demoday demoday) {
		this.demoday = demoday;
	}

	public List<DemodayCompany> getDemodayCompanies() {
		return demodayCompanies;
	}

	public void setDemodayCompanies(List<DemodayCompany> demodayCompanies) {
		this.demodayCompanies = demodayCompanies;
	}

}
