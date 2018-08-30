package com.tsb.web.controller;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.CompanyService;
import com.tsb.company.vo.CompanySearchVO;
import com.tsb.company.vo.CompanyVO;
import com.tsb.model.Company;


@Controller
@RequestMapping(value = "/api/end/company")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class CompanyCtrl {

	@Autowired
	private CompanyService companyService;

	@RequestMapping(value = "/overview")
	@ResponseBody
	public Map getCompanyByCode(@RequestParam("code") String code) {

		CompanyVO company = companyService.get(code);

		Map map = new HashMap();
		map.put("company", company);
		return map;
	}
	
	@RequestMapping(value = "/list", method={RequestMethod.POST})
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
