package com.tsb.web.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.CompaniesRelService;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/comps")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class CompaniesRelCtrl extends BaseController {
	
	@Autowired
	private CompaniesRelService crService;

	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map get(@RequestBody RequestVO request) {
		String code = (String) request.getPayload().get("code");
		
		Map map = new HashMap();
		map.put("company", crService.getByCode(code));
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map list(@RequestBody RequestVO request) {
		int id = (int) request.getPayload().get("id");
		List list = crService.get(id);
		
		Map map = new HashMap();
		map.put("comps", list);
		map.put("code", 0);
		return map;
	}
	
	
	@RequestMapping(value = "/update", method = RequestMethod.POST)
	@ResponseBody
	public Map delete(@RequestBody RequestVO request) {
		List deleteIds = (List) request.getPayload().get("deleteIds");
		List addIds = (List) request.getPayload().get("addIds");
		Integer companyId =  (Integer)request.getPayload().get("companyId");
		int userId = request.getUserid();
		
		if(deleteIds.size() > 0)
			crService.delete(deleteIds, companyId,  userId);
		
		if(addIds.size() > 0)
			crService.add(addIds, companyId,  userId);
		
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
}