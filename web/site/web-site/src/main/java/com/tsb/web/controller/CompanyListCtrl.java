package com.tsb.web.controller;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;

import com.tsb.service.CompanyListService;
import com.tsb.service.CompanyService;
import com.tsb.web.annotation.UserInfo;

@Controller
@RequestMapping(value = "/api/site/company/list")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class CompanyListCtrl {

	@Autowired
	private CompanyService companyService;
	@Autowired
	private CompanyListService companyListService;

	@UserInfo(true)
	@RequestMapping(value = "/add", method = RequestMethod.PUT)
	public void addMyList(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("listIds") String listIds, @RequestParam("companyCodes") String companyCodes)
					throws IOException {

		String[] listIdArr = listIds.split(",");
		List listIdList = new ArrayList();
		for (String s : listIdArr) {
			listIdList.add(Integer.parseInt(s));
		}

		String[] companyCodeArr = companyCodes.split(",");
		List companyCodeList = new ArrayList();
		for (String s : companyCodeArr) {
			companyCodeList.add(s);
		}

		List companyIdList = companyService.getIdsByCompanyCodes(companyCodeList);
		companyListService.createCompanyListRel(listIdList, companyIdList);
	}

}
