package com.tsb.web.controller;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.admin.service.CompanyService;
import com.tsb.model.Company;

@Controller
@RequestMapping(value = "/api/admin/company")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class CompanyCtrl {

	@Autowired
	private CompanyService companyService;

	@RequestMapping(value = "/get/id")
	@ResponseBody
	public Object getCompanyById(@RequestParam("id") Integer id) {

		return companyService.get(id);
	}
	
	@RequestMapping(value = "/source/get")
	@ResponseBody
	public List getSource(@RequestParam("id") Integer id) {

		return companyService.getSource(id);
	}
	
	@RequestMapping(value = "/get/location")
	@ResponseBody
	public Integer getLocationId(@RequestParam("name") String name) {
		
		return companyService.getLocation(name);
	}

	
	
	@RequestMapping(value = "/update", method={RequestMethod.PUT})
	@ResponseBody
	public String updateCompany(@RequestBody Company company) {
		companyService.update(company);
		
		return "{'code':0}";
	}
	
	
	
	
	@RequestMapping(value = "/list/get", method={RequestMethod.POST})
	@ResponseBody
	public List getCompaniesByIds(@RequestBody String ids) {
		String[] idArr = ids.split(",");
		List list = new ArrayList();
		for(String s: idArr){
			list.add(Integer.parseInt(s));
		}
		
		return companyService.getCompaniesByIds(list);
	}
	
	
	
	
}
