package com.tsb.web.controller;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.company.service.FundingService;
import com.tsb.model.company.Funding;
import com.tsb.model.company.FundingInvestorRel;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/funding")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class FundingCtrl extends BaseController {
	@Autowired
	private FundingService fundingSerivce;

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getFootprints(@RequestBody RequestVO request) {
		int id = (int) request.getPayload().get("id");
		List list = fundingSerivce.get(id);

		Map map = new HashMap();
		map.put("footprints", list);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/update", method = RequestMethod.POST)
	@ResponseBody
	public Map updateFunding(@RequestBody RequestVO request) throws Exception {
		ObjectMapper mapper = new ObjectMapper();
		String fundingStr = mapper.writeValueAsString(request.getPayload().get("funding"));
		Funding funding = mapper.readValue(fundingStr, Funding.class);
		fundingSerivce.updateFunding(funding);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/add", method = RequestMethod.POST)
	@ResponseBody
	public Map addFunding(@RequestBody RequestVO request) throws Exception {
		ObjectMapper mapper = new ObjectMapper();
		String fundingStr = mapper.writeValueAsString(request.getPayload().get("funding"));
		Funding funding = mapper.readValue(fundingStr, Funding.class);
		fundingSerivce.addFunding(funding);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/fir/add", method = RequestMethod.POST)
	@ResponseBody
	public Map addFir(@RequestBody RequestVO request) throws Exception {
		int userId = request.getUserid();
		ObjectMapper mapper = new ObjectMapper();
		List<FundingInvestorRel> firList = new ArrayList<FundingInvestorRel>();
		List addList = (List) request.getPayload().get("addList");
		for (int i = 0, size = addList.size(); i < size; i++) {
			String add = mapper.writeValueAsString(addList.get(i));
			FundingInvestorRel fir = mapper.readValue(add, FundingInvestorRel.class);
			firList.add(fir);
		}
		fundingSerivce.addFirs(firList,userId);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/fir/delete", method = RequestMethod.POST)
	@ResponseBody
	public Map deleteFir(@RequestBody RequestVO request) throws Exception {
		int userId = request.getUserid();
		ObjectMapper mapper = new ObjectMapper();
		List<FundingInvestorRel> firList = new ArrayList<FundingInvestorRel>();
		List descList = (List) request.getPayload().get("descList");
		for (int i = 0, size = descList.size(); i < size; i++) {
			String desc = mapper.writeValueAsString(descList.get(i));
			FundingInvestorRel fir = mapper.readValue(desc, FundingInvestorRel.class);
			firList.add(fir);
		}
		fundingSerivce.deleteFirs(firList,userId);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/delete", method = RequestMethod.POST)
	@ResponseBody
	public Map deleteFunding(@RequestBody RequestVO request) throws Exception {
		int userId = request.getUserid();
		List<Integer> ids = (List<Integer>) request.getPayload().get("ids");
		fundingSerivce.deleteFundings(ids,userId);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/new/funding", method = RequestMethod.POST)
	@ResponseBody
	public Map newFunding(@RequestBody RequestVO request) throws Exception {
		int userId = request.getUserid();
		ObjectMapper mapper = new ObjectMapper();
		String fundingStr = mapper.writeValueAsString(request.getPayload().get("funding"));
		Funding funding = mapper.readValue(fundingStr, Funding.class);
		List<FundingInvestorRel> firList = new ArrayList<FundingInvestorRel>();
		List firListStr = (List) request.getPayload().get("firList");
		for (int i = 0, size = firListStr.size(); i < size; i++) {
			String add = mapper.writeValueAsString(firListStr.get(i));
			FundingInvestorRel fir = mapper.readValue(add, FundingInvestorRel.class);
			firList.add(fir);
		}
		fundingSerivce.addFundingAndFirList(funding,firList,userId);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

}