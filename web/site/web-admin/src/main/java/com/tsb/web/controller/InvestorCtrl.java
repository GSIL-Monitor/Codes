package com.tsb.web.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.admin.dao.read.InvestorReadDao;
import com.tsb.admin.dao.read.source.SourceInvestorReadDao;
import com.tsb.admin.service.InvestorService;
import com.tsb.model.Investor;
import com.tsb.model.source.SourceInvestor;

@Controller
@RequestMapping(value = "/api/admin/investor")
public class InvestorCtrl {

	@Autowired
	private InvestorService investorService;
	@Autowired
	private InvestorReadDao investorReadDao;
	@Autowired
	private SourceInvestorReadDao sourceInvestorReadDao;
	
	
	@SuppressWarnings({ "rawtypes", "unchecked" })
	@RequestMapping(value = "/add", method={RequestMethod.PUT})
	@ResponseBody
	public Map addInvestor(@RequestBody Investor v) {
		investorService.addInvestor(v);
		HashMap map = new HashMap();
		map.put("code", 0);
		map.put("investor", v);
		return map;
	}
	
	@SuppressWarnings({ "rawtypes", "unchecked" })
	@RequestMapping(value = "/update", method={RequestMethod.PUT})
	@ResponseBody
	public Map updateInvestor(@RequestBody Investor v) {
		investorService.updateInvestor(v);
		HashMap map = new HashMap();
		map.put("code", 0);
		map.put("investor", v);
		return map;
	}
	
	@SuppressWarnings({ "rawtypes", "unchecked" })
	@RequestMapping(value = "/getwithsources")
	@ResponseBody
	public Map getWithSources(@RequestParam("id") Integer id) {
		Investor investor = investorReadDao.getById(id);
		List<SourceInvestor> sources = sourceInvestorReadDao.listByInvestorId(id);
		HashMap map = new HashMap();
		map.put("investor", investor);
		map.put("sources", sources);
		return map;
	}
	
	@RequestMapping(value = "/delete", method={RequestMethod.PUT})
	@ResponseBody
	public String deleteInvestor(@RequestBody Investor v) {
		investorService.deleteInvestor(v.getId());
		return "{'code':0}";
	}
}
